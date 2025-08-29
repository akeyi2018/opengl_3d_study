import glfw
from OpenGL.GL import *
import time
import ctypes

def main():
    # GLFWの初期化
    if not glfw.init():
        return
    
    # ウィンドウ作成
    window = glfw.create_window(800, 600, "GPU Performance Test", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    # シェーダ作成
    vertex_shader_source = """
    #version 330 core
    layout(location = 0) in vec3 aPos;
    void main() {
        gl_Position = vec4(aPos, 1.0);
    }
    """

    fragment_shader_source = """
    #version 330 core
    out vec4 FragColor;
    void main() {
        FragColor = vec4(1.0);
    }
    """

    def compile_shader(source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        # エラーチェック省略
        return shader

    # シェーダプログラム
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # 三角形の頂点データ
    vertices = [
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0
    ]

    import numpy as np
    vertices = np.array(vertices, dtype=np.float32)

    # VBOとVAOの設定
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # GPUタイマー用のクエリオブジェクト
    query = glGenQueries(1)
    query_id = query[0]

    # 描画前の準備
    glClearColor(0.2, 0.3, 0.3, 1.0)

    # パフォーマンス計測開始
    glBeginQuery(GL_TIME_ELAPSED, query_id)

    # 描画処理
    glUseProgram(shader_program)
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 3)

    # 描画完了
    glEndQuery(GL_TIME_ELAPSED)

    # GPU処理完了待ち
    done = False
    while not done:
        done = glGetQueryObjectiv(query_id, GL_QUERY_RESULT_AVAILABLE)
        time.sleep(0.001)  # 少し待つ

    # 経過時間取得（ナノ秒）
    time_elapsed = ctypes.c_uint64()
    glGetQueryObjectui64v(query_id, GL_QUERY_RESULT, ctypes.byref(time_elapsed))
    print(f"GPU rendering time: {time_elapsed.value / 1e6:.3f} ms")

    # ウィンドウのメインループ（描画し続ける場合はここに追加）
    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()

    # 後片付け
    glDeleteQueries(1, [query_id])
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()
