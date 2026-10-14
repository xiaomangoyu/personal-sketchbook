# 随手画 · Personal Sketchbook

**用几笔颜色，画出具体的形状。**

一个可继续修改的个人绘画 skill。AI 帮忙构思和编写绘图代码，Python 用笔触画出图片；你看图、选方向，再局部调整。支持彩色线描、钢笔淡彩、铅笔与蜡笔。

> An editable sketchbook for loose coloured lines and small stories. AI helps plan and code; Python renders the marks. Keep the picture, its source, and room to revise.

## 最近画的四种水果

这组用 pencil-case 原版钢笔笔刷绘制，颜色主要来自松散的有色短笔，背景保持纯白。不同果实有不同的形体和表面，不能只给同一套排线换个颜色。

<table>
<tr>
<td width="50%"><a href="examples/studies/loose-fruits-v2/mandarin/artwork.png"><img src="examples/studies/loose-fruits-v2/mandarin/artwork.png" alt="整颗剥皮的橘子：鼓起的果瓣、弯曲的纵缝，果皮向外翻开。" width="100%"></a><br><strong>整颗剥皮的橘子</strong><p>鼓起的果瓣、弯曲的纵缝，果皮向外翻开。</p><a href="examples/studies/loose-fruits-v2/mandarin/scene.json">场景 JSON</a> · <a href="examples/generators/loose_fruit_studies.py">生成脚本</a></td>
<td width="50%"><a href="examples/studies/loose-fruits-v2/pear/artwork.png"><img src="examples/studies/loose-fruits-v2/pear/artwork.png" alt="歪一点的梨：细颈偏向一侧，黄绿短笔围着饱满的下腹转。" width="100%"></a><br><strong>歪一点的梨</strong><p>细颈偏向一侧，黄绿短笔围着饱满的下腹转。</p><a href="examples/studies/loose-fruits-v2/pear/scene.json">场景 JSON</a> · <a href="examples/generators/loose_fruit_studies.py">生成脚本</a></td>
</tr>
<tr>
<td width="50%"><a href="examples/studies/loose-fruits-v2/peach/artwork.png"><img src="examples/studies/loose-fruits-v2/peach/artwork.png" alt="带叶的桃子：两侧不等大，杏黄过渡到粉红，果缝弯着向下。" width="100%"></a><br><strong>带叶的桃子</strong><p>两侧不等大，杏黄过渡到粉红，果缝弯着向下。</p><a href="examples/studies/loose-fruits-v2/peach/scene.json">场景 JSON</a> · <a href="examples/generators/loose_fruit_studies.py">生成脚本</a></td>
<td width="50%"><a href="examples/studies/strawberry-texture-v3/artwork.png"><img src="examples/studies/strawberry-texture-v3/artwork.png" alt="一颗草莓：短碎色笔、淡金色籽与小凹陷，保留纸白。" width="100%"></a><br><strong>一颗草莓</strong><p>短碎色笔、淡金色籽与小凹陷，保留纸白。</p><a href="examples/studies/strawberry-texture-v3/scene.json">场景 JSON</a> · <a href="examples/generators/strawberry_texture_study.py">生成脚本</a></td>
</tr>
</table>

### 同一颗草莓，换一种表面

左边的长排线偏向纤维感；右边改成短碎笔触，把籽周围的小凹陷留出来。只改果皮与籽两个对象，叶子、轮廓和投影等其余 14 个图层的哈希保持一致。

<table><tr>
<td width="50%"><img src="examples/studies/loose-fruits-v2/strawberry/artwork.png" alt="修改前：草莓使用较长的排线" width="100%"><br>修改前 · 长排线</td>
<td width="50%"><img src="examples/studies/strawberry-texture-v3/artwork.png" alt="修改后：短碎色笔与籽窝" width="100%"><br>修改后 · 短笔与籽窝</td>
</tr></table>

[彩色线描的画法](references/coloured-linework.md) · [水彩渐变与晕染](references/light-watercolour.md) · [草莓修改脚本](examples/generators/strawberry_texture_study.py)

## 之前的小故事

<details>
<summary>展开早期场景画廊与纸袋猫试稿</summary>

这些版本保留用于比较构图、媒介和用笔，不作为新画必须遵循的固定风格。

<a href="examples/studies/breakfast-cat-v2/artwork.png"><img src="examples/studies/breakfast-cat-v2/artwork.png" alt="轻墨、局部淡彩与留白的纸袋猫" width="460"></a>

[纸袋猫线稿](examples/studies/breakfast-cat-v2/ink-only/artwork.png) · [场景 JSON](examples/studies/breakfast-cat-v2/scene.json) · [生成脚本](examples/generators/breakfast_cat_study.py)

<!-- GALLERY:START -->
<table>
<tr>
<td width="50%"><a href="examples/gallery/breakfast-cat/artwork.png"><img src="docs/images/breakfast-cat-thumb.jpg" alt="猫把早餐纸袋当成了窝" width="100%"></a><br><strong>猫把早餐纸袋当成了窝</strong><br>铅笔 · 淡彩<p>画一只把早餐纸袋当成窝的小猫，只露出脑袋和一只爪。</p><a href="examples/gallery/breakfast-cat/scene.json">场景 JSON</a> · <a href="examples/generators/breakfast_cat.py">生成脚本</a></td>
<td width="50%"><a href="examples/gallery/rainy-cafe/artwork.png"><img src="docs/images/rainy-cafe-thumb.jpg" alt="雨停前的街角咖啡店" width="100%"></a><br><strong>雨停前的街角咖啡店</strong><br>钢笔 · 淡彩<p>画一间雨里的街角咖啡店，暖灯亮着，门口撑着一把伞。</p><a href="examples/gallery/rainy-cafe/scene.json">场景 JSON</a> · <a href="examples/generators/rainy_cafe.py">生成脚本</a></td>
</tr>
<tr>
<td width="50%"><a href="examples/gallery/orange-market/artwork.png"><img src="docs/images/orange-market-thumb.jpg" alt="周末市场的橘子摊" width="100%"></a><br><strong>周末市场的橘子摊</strong><br>蜡笔 · 铅笔<p>画一个热闹的橘子摊，一只橘子悄悄滚出了果箱。</p><a href="examples/gallery/orange-market/scene.json">场景 JSON</a> · <a href="examples/generators/orange_market.py">生成脚本</a></td>
<td width="50%"><a href="examples/gallery/windy-camp/artwork.png"><img src="docs/images/windy-camp-thumb.jpg" alt="风把山顶帐篷吹歪了一点" width="100%"></a><br><strong>风把山顶帐篷吹歪了一点</strong><br>蜡笔 · 铅笔<p>画山顶有风的露营地，帐篷偏在一旁，草和云都朝同一个方向。</p><a href="examples/gallery/windy-camp/scene.json">场景 JSON</a> · <a href="examples/generators/windy_camp.py">生成脚本</a></td>
</tr>
<tr>
<td width="50%"><a href="examples/gallery/book-whale/artwork.png"><img src="docs/images/book-whale-thumb.jpg" alt="旧书里游出一条鲸鱼" width="100%"></a><br><strong>旧书里游出一条鲸鱼</strong><br>淡彩 · 钢笔<p>画一条从翻开的旧书里游出来的鲸鱼，让书页像海浪一样托住它。</p><a href="examples/gallery/book-whale/scene.json">场景 JSON</a> · <a href="examples/generators/book_whale.py">生成脚本</a></td>
<td width="50%"><a href="examples/gallery/bicycle-workshop/artwork.png"><img src="docs/images/bicycle-workshop-thumb.jpg" alt="修车铺午后的最后一束光" width="100%"></a><br><strong>修车铺午后的最后一束光</strong><br>钢笔 · 排线<p>画修车铺里一辆旧自行车的局部，一束暖光照到车轮和木工作台。</p><a href="examples/gallery/bicycle-workshop/scene.json">场景 JSON</a> · <a href="examples/generators/bicycle_workshop.py">生成脚本</a></td>
</tr>
</table>
<!-- GALLERY:END -->

</details>

## 画完了，还能继续画

| 你想做的事 | 随手画怎么帮忙 |
| --- | --- |
| 一张画里换几支笔 | 钢笔、铅笔、蜡笔、淡彩和排线可以混用；轮廓、暗面和纸纹各有轻重。 |
| 改一个物件，不重来整幅 | 每个物件和笔触有固定 ID。固定画布、纸纹和种子后，未改对象的笔迹保持不变。 |
| 留下可以接着画的版本 | 同时保存 PNG、场景 JSON、透明对象图层和渲染记录；也保留生成场景的 Python 脚本。 |

### 比如，只给雨伞换个颜色

左边是原画，右边只改了 `umbrella` 对象里的填色。店面、人物、积水和其他物件的源数据没有改动；[对照记录](examples/edits/blue-umbrella/comparison.json) 按导出的图层文件逐一比较 SHA-256。

![局部修改对照：只改变雨伞颜色](docs/images/local-edit.jpg)

[原始场景](examples/gallery/rainy-cafe/scene.json) · [修改后的场景](examples/edits/blue-umbrella/scene.json) · [修改后大图](examples/edits/blue-umbrella/artwork.png)

换位置、改形状或调整轻重也可以沿着同一个 ID 继续改；如果改变遮挡关系，仍需要一起检查邻近物件。

## 五支笔，各有用处

下面是从早期六幅场景中截取的实际局部；本页水果主要使用原版 `ink`，只有接触投影带少量淡彩。

![实际作品中的钢笔、铅笔、蜡笔、淡彩和排线细节](docs/images/brushes.jpg)

| 笔触 | 用在什么地方 |
| --- | --- |
| `ink` 钢笔 | 明确的结构与暗边，带轻重、断墨和收笔。 |
| `pencil` 铅笔 | 找形、轻轮廓和柔和细节，让纸纹透出来。 |
| `wax` 蜡笔 | 有方向的颗粒色块，留一点纸缝。 |
| `wash` 淡彩 | 薄色、水痕与不均匀的边缘沉淀。 |
| `hatch` 排线 | 用疏密和方向解释暗面，不把整件东西涂黑。 |

流程很简单：**描述想画的东西 → AI 安排场景与笔触 → Python 渲染图片和图层 → 看图，再改。**

手感既来自用笔，也来自具体的观察：纸袋哪儿被压皱、猫的爪子搭在哪里、风往哪个方向吹。给每条线加噪声，不能替代这些判断。

## 先画出第一张

本次发布验证环境：Python 3.11.1、Pillow 12.2.0、NumPy 2.4.4。使用隔离环境运行：

```bash
git clone https://github.com/xiaomangoyu/personal-sketchbook.git
cd personal-sketchbook
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/render.py examples/studies/strawberry-texture-v3/scene.json --out output/first-drawing
```

打开 `output/first-drawing/artwork.png` 就能看到结果。这条命令直接重放已有场景，不需要模型或 API key。Windows 下对应的 Python 路径是 `.venv\Scripts\python.exe`；本次未验证 Windows 运行。

### 当作 Codex skill 使用

把仓库文件夹放到 `~/.codex/skills/personal-sketchbook/`。如果已有同名 skill，保留自己的修改后再更新。让 Codex 使用刚才创建的 Python 环境，然后说：

> 用 `$personal-sketchbook` 画一只趴在雨天窗台上的猫。颜色暖一点，窗外只留几笔雨，不加文字。

也可以继续说：

> 只把猫旁边的杯子改成砖红色，其他地方保留。

[SKILL.md](SKILL.md) 是给 AI 的创作与操作说明；[构图与用笔](references/art-direction.md) 讲看图时怎么判断，[绘图接口](references/render-api.md) 讲参数和数据格式。

### 用 Python 继续改

水果例子可以重新生成，也可以只改草莓纹理：

```bash
.venv/bin/python examples/generators/loose_fruit_studies.py --out output/fruits
.venv/bin/python examples/generators/strawberry_texture_study.py --out output/strawberry
```

需要自己组织物件时，可以使用 [`scene_tools.py`](scripts/scene_tools.py) 的曲线、椭圆、变换和对象工具。它生成的仍然是 `version: 1` 场景，和现有渲染命令兼容。

```python
from scene_tools import Scene, ellipse

s = Scene("一片叶子", width=700, height=800, seed=42)
leaf = s.object("leaf", "叶片")
leaf.fill("color", ellipse(350, 370, 50, 125, rotate=25),
          (118, 148, 87), opacity=0.5)
leaf.line("vein", [[300, 490], [350, 370], [392, 273]],
          width=1.6, opacity=0.7)
s.save("leaf.json")
```

第一条生成水果初稿（含草莓修改前的版本）；第二条基于保留的草莓场景，只更新果皮与籽图层。也可给第一条加 `--fruit mandarin`、`pear` 或 `peach` 单独出图。

从脚本使用时将仓库的 `scripts` 目录加入 Python 的模块搜索路径；六份生成脚本展示了不依赖当前工作目录的写法。

## 一张画会留下什么

```text
my-drawing/
├── artwork.png       完整图片
├── scene.json        物件、几何、颜色与固定 ID
├── manifest.json     依赖版本、代码哈希、图层哈希和渲染提醒
└── layers/
    ├── _paper.png    纸面
    └── ...png        每个物件的透明图层
```

仓库保留展示原图、场景、生成脚本与记录；体积较大的对象图层可以用同一命令重新生成，不重复提交。相同代码、依赖版本和场景可复现；跨版本不承诺像素完全一致。

原来的[桌面淡彩](assets/examples/quiet-desk-preview.png)和[窗边盆栽](assets/examples/window-plant-preview.png)也保留着，适合从简单场景开始。

## 目前的边界

这是程序化绘画工具。新画面的构图和造型仍依赖 AI 写出的几何及看图修改；复杂人体、精确肖像和严谨透视需要额外检查。纸纹与水彩是视觉近似，成品仍可能带有程序插画的规整感。

当前输出静态图片和图层；没有图形编辑器、自动照片识别或连续落笔视频。作品属于 AI 辅助创作，不冒充真人手绘，也不保证“完全没有 AI 感”。

## 来源与许可

这个项目从 [盏与 North 的 pencil-case](https://github.com/Qizhan7/pencil-case) 学习程序化蜡笔与钢笔淡彩的思路，保留两份原始笔刷代码，并增加了统一场景、纸面相关笔触、局部编辑、构图指南、水果材质试稿及六幅故事场景。

原作者：**Sienna Qi（戚盏）与 North**。改编与维护：**[xiaomangoyu](https://github.com/xiaomangoyu)**，使用 AI 辅助开发与创作。

沿用 **[PolyForm Noncommercial 1.0.0](LICENSE)**，适用于个人爱好、学习和其他许可允许的非商业使用。复制或分享时保留许可和 Required Notice；商业用途按原许可取得授权。完整来源见 [NOTICE.md](NOTICE.md)。

## 复现与检查

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_showcase.py --render-scenes
.venv/bin/python scripts/check_release.py --render
```

`build_showcase.py --render-scenes` 重建内置六幅样图及其图层，再生成封面、缩略图、笔触局部和修改对照；它会覆盖内置展示输出。个人作品请单独保存。独立运行生成脚本时，重复使用同一输出目录要求显式 `--overwrite`；想保留旧版就换一个 `--out` 目录。
