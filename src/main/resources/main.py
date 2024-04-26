import com.badlogic.gdx.Gdx as Gdx
import com.badlogic.gdx.ApplicationAdapter as ApplicationAdapter
import com.badlogic.gdx.Input as Input
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application as Lwjgl3Application
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration as Lwjgl3ApplicationConfiguration
import com.badlogic.gdx.graphics.OrthographicCamera as OrthographicCamera
import com.badlogic.gdx.graphics.GL20 as GL20
import com.badlogic.gdx.graphics.Color as Color
import com.badlogic.gdx.graphics.Texture as Texture
import com.badlogic.gdx.graphics.Pixmap as Pixmap
import com.badlogic.gdx.graphics.g2d.SpriteBatch as SpriteBatch
import com.badlogic.gdx.graphics.g2d.BitmapFont as BitmapFont
import com.badlogic.gdx.graphics.g2d.TextureRegion as TextureRegion
import com.badlogic.gdx.math.Polygon as Polygon
import com.badlogic.gdx.math.MathUtils as MathUtils
import com.badlogic.gdx.math.Vector2 as Vector2
import com.badlogic.gdx.utils.ScreenUtils as ScreenUtils
import java.lang.Math as Math
import java.lang.Integer as Integer
import space.earlygrey.shapedrawer.ShapeDrawer as ShapeDrawer
from java.lang import Float, Double

MAX_BUBBLES = 100
INSTANCE = None


class GameObject:
    def __init__(self, position=Vector2()):
        self.position = position


class Player(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self.level = 1
        self.score = 0
        self.move = 0
        self.radius = 24
        self.hp = 5
        self.rotation = Float(0.0)  # Degrees

        self.__tmp = Vector2()

        vertices = [
            -10, 12,
            0, -12,
            10, 12,
            0, 6,
        ]

        self.__arrow = Polygon(vertices)

    def collide(self, other):
        if other.type != BubbleType.DAMAGE:
            self.score += other.speed * other.radius
        elif not other.dead:
            self.hp -= 1
            if self.hp <= 0:
                # noinspection PyUnresolvedReferences
                INSTANCE.game_over()

        other.dead = True

        if self.score - (self.level * 10000) > 10000:
            self.level += 1

    def render(self, shapes):
        rotation = 0
        move = 0

        if Gdx.input.isKeyPressed(Input.Keys.D) or Gdx.input.isKeyPressed(Input.Keys.RIGHT):
            rotation += 2
        if Gdx.input.isKeyPressed(Input.Keys.A) or Gdx.input.isKeyPressed(Input.Keys.LEFT):
            rotation -= 2
        if Gdx.input.isKeyPressed(Input.Keys.W) or Gdx.input.isKeyPressed(Input.Keys.UP):
            move += 2
        if Gdx.input.isKeyPressed(Input.Keys.S) or Gdx.input.isKeyPressed(Input.Keys.DOWN):
            move -= 2

        self.position.add(MathUtils.cos(Float(self.rotation * MathUtils.degRad)) * move,
                          MathUtils.sin(Float(self.rotation * MathUtils.degRad)) * move)
        self.position.x = Math.min(Math.max(self.position.x, 0), Gdx.graphics.getWidth())
        self.position.y = Math.min(Math.max(self.position.y, 0), Gdx.graphics.getHeight())
        self.rotation += rotation

        shapes.setColor(Color(1, 0, 0, 1))
        shapes.filledCircle(self.position.x, self.position.y, self.radius)
        self.__arrow.setPosition(self.position.x, self.position.y)
        self.__arrow.setRotation(self.rotation + 90)

        shapes.setColor(Color(1, 1, 1, 1))
        trans_vertices = self.__arrow.getTransformedVertices()
        shapes.filledPolygon(trans_vertices)


class BubbleType:
    NORMAL = 0
    DAMAGE = 1


class Bubble(GameObject):
    # noinspection PyInitNewSignature
    def __init__(self, radius, speed, type_=BubbleType.NORMAL):
        GameObject.__init__(self,
                            Vector2(Gdx.graphics.getWidth() + radius, MathUtils.random(0, Gdx.graphics.getHeight())))
        self.radius = radius
        self.speed = speed
        self.type = type_
        self.dead = False

    # noinspection PyTypeChecker
    def render(self, shapes):
        if self.type == BubbleType.NORMAL:
            shapes.setColor(Color.WHITE)
            shapes.circle(self.position.x, self.position.y, self.radius, 4)
        elif self.type == BubbleType.DAMAGE:
            shapes.setColor(Color(Float(1.0), Float(0.1), Float(0.2), Float(1.0)))  # 1.0, 0.1, 0.2, 1.0))
            shapes.circle(self.position.x, self.position.y, self.radius, 5)

        self.position.x -= self.speed


class QBubblesGDX(ApplicationAdapter):
    def __init__(self):
        self.gameOver = False
        self.heartEmptyTex = None
        self.heartTex = None
        self.gameOverTex = None
        self.player = None
        self.shapes = None
        self.camera = None
        self.batch = None
        self.font = None
        self.time = 0.0

        self.lastDrop = 0
        self.width = 800
        self.height = 480
        self.bubbles = []

    def create(self):
        global INSTANCE
        INSTANCE = self

        self.camera = OrthographicCamera()
        self.camera.setToOrtho(False, self.width, self.height)
        self.batch = SpriteBatch()

        self.player = Player()
        self.heartTex = Texture(Gdx.files.internal("assets/heart.png"))
        self.heartEmptyTex = Texture(Gdx.files.internal("assets/heart_empty.png"))
        self.gameOverTex = Texture(Gdx.files.internal("assets/game_over.png"))

        white = Pixmap(1, 1, Pixmap.Format.RGB888)
        white.drawPixel(0, 0, Integer.parseUnsignedInt("ffffffff", 16))

        self.batch = SpriteBatch()
        self.shapes = ShapeDrawer(self.batch, TextureRegion(Texture(white)))
        self.font = BitmapFont(True)

    def render(self):
        ScreenUtils.clear(Color(0x0080ffff if not self.gameOver else 0x404040ff))
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT)

        self.batch.begin()
        self.render_game()
        self.render_hud()
        self.batch.end()

    def game_over(self):
        self.gameOver = True
        self.bubbles = []

    def render_hud(self):
        for idx in range(0, 5):
            if idx + 1 <= self.player.hp:
                self.batch.draw(self.heartTex, 8 + 56 * idx, 52, 48, -48)
            else:
                self.batch.draw(self.heartEmptyTex, 8 + 56 * idx, 52, 48, -48)

        self.font.draw(self.batch, "Score: " + str(self.player.score), 341, 10)
        self.font.draw(self.batch, "Level: " + str(self.player.level), 341, 30)

        if self.gameOver:
            self.batch.draw(self.gameOverTex, Gdx.graphics.getWidth() / 2 - 64, Gdx.graphics.getHeight() / 3 + 64, 128,
                            -128)

    def render_game(self):
        for bubble in self.bubbles:
            bubble.render(self.shapes)
            if bubble.position.dst(self.player.position) < self.player.radius + bubble.radius:
                self.player.collide(bubble)
                if self.gameOver:
                    break
                self.bubbles.remove(bubble)
            if bubble.position.x < -bubble.radius:
                self.bubbles.remove(bubble)

        if not self.gameOver:
            self.player.render(self.shapes)
            if len(self.bubbles) < MAX_BUBBLES:
                type_ = BubbleType.NORMAL
                if MathUtils.random(0, 30) == 0:
                    type_ = BubbleType.DAMAGE
                bubble = Bubble(MathUtils.random(24, 56), MathUtils.random(1, 4), type_)
                self.bubbles.append(bubble)

        self.time += Gdx.graphics.getDeltaTime()

    # noinspection PyUnusedLocal
    def resize(self, width, height):
        self.batch.setProjectionMatrix(
            self.batch.getProjectionMatrix().setToOrtho(0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight(), 0, 0,
                                                        1000000))

        self.player.position.set(Gdx.graphics.getWidth() / 2, Gdx.graphics.getHeight() / 2)
        self.bubbles = []

        for i in range(0, MAX_BUBBLES):
            type_ = BubbleType.NORMAL
            if MathUtils.random(0, 30) == 0:
                type_ = BubbleType.DAMAGE
            bubble = Bubble(MathUtils.random(24, 56), MathUtils.random(1, 4), type_)
            self.bubbles.append(bubble)
            bubble.position = Vector2(MathUtils.random(0, Gdx.graphics.getWidth()),
                                      MathUtils.random(0, Gdx.graphics.getHeight()))

    def dispose(self):
        self.batch.dispose()


def launch():
    cfg = Lwjgl3ApplicationConfiguration()
    cfg.setTitle("QBubbles - PyLibGDX Edition")
    cfg.setResizable(False)
    cfg.setForegroundFPS(60)
    cfg.setWindowedMode(1280, 720)
    cfg.setBackBufferConfig(8, 8, 8, 12, 16, 0, 16)

    Lwjgl3Application(QBubblesGDX(), cfg)


def main():
    try:
        launch()
    except Exception as e:
        throw = e.__traceback__
        while throw is not None:
            import sys
            print(throw.tb_lineno, throw.tb_frame.f_code.co_filename, throw.tb_frame.f_code.co_name, file=sys.stderr)
            throw = throw.tb_next

        print(e.__class__.__name__, e, file=sys.stderr)


if __name__ == '__main__':
    print("QBubbles - PyLibGDX Edition")
    main()

print("__name__", __name__)
