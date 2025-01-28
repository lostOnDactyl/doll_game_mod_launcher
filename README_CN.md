(Translated with ChatGPT lol)

# 娃娃游戏启动器
非常简陋，仅用大约四小时完成。后续会重新设计大部分功能，但欢迎提交问题或 PR（特别是关于 mods 页面，我在这里有点迷茫）。下个版本将有自动更新按钮，但这个版本没有，哈哈。

你也可以通过 Discord 联系我 @deuil0002。

## 计划
- 更好的 3DMigoto 集成（支持按键绑定）
- 启动器中为 mods 提供可自定义的开关
- 显示哈希冲突
- 改善 mods 页面，让其更美观且功能更完善（可能某一天会加入缩略图，但暂时不敢奢望）

# 安装说明
这些是针对 Windows 的安装说明，因为大多数人是在 Windows 上运行第五人格。需要 Python，我用的是 3.13。关于安装 Python，你可以找到比我能写的更好的教程。

你需要一个功能正常的 3DMigoto。如果你还没有为第五人格设置好它，我不会帮你配置，所以你应该先解决这个问题。

1. 克隆此仓库或下载 .zip 文件并解压
2. 在文件夹内右键并选择“在终端中打开”
3. 依次运行以下命令：
- `py -m venv venv`
- `Set-ExecutionPolicy Unrestricted -Scope Process`
- `venv\Scripts\activate`
- `pip install -r requirements.txt`
4. 启动时运行 `python main.py`（你必须在 venv 中！）

如果你不想使用虚拟环境，按照步骤 1-2，然后执行以下操作代替步骤 3 和 4：

3. 运行
- `py -m pip install -r requirements.txt`
4. 启动时运行 `py main.py`

## 设置
在使用此启动器之前，你需要先设置文件。前往“设置”选项卡。
1. 在“游戏可执行文件”中填写你的 `dwrg.exe` 路径（例如：我的路径是 "C:/IdentityV2/dwrg.exe"）
2. 同样填写 3DMigoto 可执行文件的路径，以及 mods 文件夹的路径（显然这不会是 `.exe` 文件）
3. 点击保存，然后点击“重新加载”
现在你应该拥有核心功能了。通过前往主页并启动游戏来测试。如果要将语言更改为中文，可以选择 cnS，保存，然后重新加载 :)

# Mod 指南
如果某个 mod 没有 mod.json 文件，它会默认加载（但你无法在启动器中看到它）。

这仅与您希望创建与启动器兼容的 mod 或使 mod 能够与之兼容相关。我已经包含了一个脚本来帮助你。此脚本会将 .ini 文件转换为 .json 文件，只需你添加一些参数。

## Mod“类型”
我定义了两种主要的 mod 类型：“skinmod”和……不是 skinmod。这并不难理解。skinmod 是覆盖游戏中的对象的任何东西，而不是 skinmod 则不是。这意味着覆盖火箭椅、工具和皮肤是 skinmod，而炫酷的着色器不是。

Skinmod 有两种子类型：角色和对象。角色会验证你提供的角色名称是否符合我制作的角色列表；对象不会。如果你使用工具，也请确保使用角色类型——律师的地图和律师的皮肤 mod 都归在他的角色下。

## 目标
目标是你想覆盖的主要缓冲区。例如，皮肤的索引缓冲区——而不是单个纹理。不用担心，当你在文件中看到它时会更容易理解。

## 准备你的 .ini
以下是我创建的一个 mod 的 .ini 示例。我们将使用此文件来准备处理。我已排除了 Resources 部分以使其更易阅读；你无需在那里写任何新内容。

```ini
; 简单的武器覆盖 mod

; 默认信号枪 ib 哈希
[TextureOverrideCoordGun]
hash = b74ef525
ib = ResourceHLGunIB
vb0 = ResourceHLGunVB0
handling = skip
drawindexed = auto

[TextureOverrideFlareGunDefault]
hash = d42fe57a
this = ResourceHLGunTexture

[TextureOverrideFlareGunNormal]
hash = 1039a896
this = ResourceHLGunNormal
```

首先，我们将添加一些前言信息。你可以将 mod 的 id 设置为任意值，但尽量保持唯一性。作者填写你的用户名——你可以有多个 `; author=` 行，它会将其添加到作者数组中，而不是覆盖之前的值。

由于我们在修改工具，因此它属于 `; skinmod=True`。版本号可以随意填写，这取决于你如何跟踪你的 mod，或者是否会进一步开发它。`； desc=` 是描述，相信很好理解。

（希望当你看到这段文字时，我已经更新了仓库中的解析器以允许等号之间有空格……）

```ini
; 简单的武器覆盖 mod

; MOD 管理器信息
; ---------------------------------------------
; id=hlglock
; author=dactyl
; skinmod=True
; version=1
; desc=将协调员的默认枪替换为原版半条命格洛克

; 默认信号枪 ib 哈希
; ...
```

此 mod 的主要目标是协调员的信号枪。如果我的文件同时包含协调员的服装和信号枪，我将有两个目标。

在包含你标记为目标的缓冲区的部分上方，添加角色名称、类型（我倾向于根据你在做什么使用工具或身体），以及一个备注，以便以后不至于抓狂。

```ini
; 默认信号枪 ib 哈希
; char=coordinator type=tool note=协调员的信号枪 ib
[TextureOverrideCoordGun]
hash = b74ef525
ib = ResourceHLGunIB
vb0 = ResourceHLGunVB0
handling = skip
drawindexed = auto
```

对于角色皮肤 mod，这就是你必须做的一切。你不需要制作任何非目标缓冲区。

### 如果我在修改对象或着色器呢？
对于对象，只需在前言下添加 `; OBJECT = true`。然后，用 `object=` 替换 `; char=`。类型可以是任何你喜欢的内容，但这个约定对我来说很好：

```ini
; object=ROCKET_CHAIR ; type=skin ; note=所有地面火箭椅
[TextureOverrideChair]
```

虽然我确实包含了一种自动处理着色器的方法，例如：

```ini
; id=my_sexy_shader
; desc=让你的电脑爆炸
; author=dactyl
; version=1
; SHADER=true
```
我并未对此进行广泛测试，你可能需要在 .json 中填写一些内容。着色器 .json 不仅包含缓冲区哈希，还包括例如 `XXXXXX-ps` 或 `XXXXXX-vs`。显然没有目标。

## 将你的 .ini 转换为 mod.json
以上的一切都是为了准备将 .ini 转换为 mod.json。这真的不难。我们将使用启动器根目录中的 `INI_PARSE.py` 脚本。

`INI_PARSE.py` 有一个必需参数——输入的 ini 文件。默认情况下，它会将 mod.json 输出到该 ini 文件的同一文件夹中。

```bash
> py INI_PARSE.py "C:\Users\Owner\3DMigoto\Mods\SexyMod\sexy.ini"
```

不过，你也可以使用 `--output_directory` 参数指定输出位置。我不推荐这样做，因为如果 .ini 和 mod.json 不在同一目录下，你会遇到加载器的一些错误，不过如果你想这样做，可以试试。

```bash
> py INI_PARSE.py "C:\Users\Owner\3DMigoto\Mods\SexyMod\sexy.ini" --output_directory "C:\Users\Owner\Desktop\ModJsons"
```

默认情况下，启动器会查看你指定 Mods 文件夹中的每个子目录，并搜索 mod.json。

请检查你的 mod.json 以确保一切正常！你也可以在启动器打开时对其进行更改，然后点击“重新加载”以重新加载所有内容。

[Mod 参考链接](https://gamebanana.com/mods/570866)，其中包含一个 mod.json 和格式良好的 .ini 文件，你可以用来测试你的 mod。