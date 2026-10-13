# 可编辑绘图接口

## 运行和输出

```bash
python3 "<skill>/scripts/render.py" scene.json --validate-only
python3 "<skill>/scripts/render.py" scene.json --out drawing-v01
```

输出 `artwork.png`、原始 `scene.json`、`manifest.json`、`layers/_paper.png` 和各物件的透明 PNG。按照 JSON 对象顺序，先纸层再逐一 alpha composite，能重新得到整图。不同物件按绘制顺序覆盖，物件内部按 marks 顺序覆盖。要让另一个物体穿插在前后两处，可分成前后两个对象。

非空输出目录默认拒绝覆盖。`--overwrite` 只接受带本渲染器 manifest 的目录，移除上次记录的旧对象图层并重写生成物，其他文件保留。正常创作保留版本。

## 场景

```json
{
  "version": 1,
  "title": "一片叶子",
  "seed": 42,
  "canvas": {"width": 700, "height": 800, "paper": [247,245,238], "grain": 0.3},
  "objects": [{
    "id": "leaf", "name": "叶片", "translate": [0,0], "visible": true,
    "marks": [
      {"id":"color", "kind":"wash", "polygon":[[270,430],[285,300],[365,255],[380,365],[270,430]], "color":[128,153,98], "opacity":0.35, "edge":0.2, "bleed":2},
      {"id":"vein", "kind":"ink", "points":[[255,465],[300,390],[345,305]], "color":[75,85,62], "width":1.6, "wobble":0.55, "smooth":true, "opacity":0.7}
    ]
  }]
}
```

- 单位是最终图片像素，不是归一化坐标。画布 64–4096 整数像素，每张不超过 800 万像素。放大画布时同步考虑坐标与笔宽，不能只改尺寸。
- `seed` 是 0–4294967295 的整数。每个 mark 的随机种子由 scene seed、object id、mark id 推导；与在列表中的序号无关。
- `id` 为 1–80 个英文字母/数字/下划线/短横线，第一位须为字母或数字；object id 场景内唯一（不区分大小写，避免文件名冲突）、mark id 对象内唯一。`name` 可写中文，id 编辑时保留。
- `translate:[dx,dy]` 平移整个对象；`visible:false` 保留数据但输出空图层。移动后接触的纸纹位置会变化，这是预期行为。
- 画布外坐标允许，用于有意裁切；需要完整主体时检查边缘。渲染器会对完全空白的可见对象发 warning，不会替代视觉审查。
- `color` 三个整数 0–255；`opacity` 0–1，0 确保无可见笔迹。数值、坐标和常用字段由渲染前校验。

## 五种笔触

| kind | 几何 | 可调字段 | 主要用途 |
|---|---|---|---|
| `ink` | `points` 至少两点 | `width`、`wobble`、`pressure`、`gaps`、`smooth`、`closed` | 有轻重和收笔的钢笔轮廓 |
| `pencil` | `points` 至少两点 | 同 ink | 纸纹可见的铅笔轻线、找形、深浅轮廓 |
| `wax` | `polygon` 至少三点 | `direction`、`density`、`grain` | 有方向、留纸缝的颗粒色块 |
| `wash` | `polygon` 至少三点 | `edge`、`bleed`、`grain` | 薄色、水痕与不均匀深边 |
| `hatch` | `polygon` 至少三点 | `angle`、`spacing`、`width` | 局部暗面、排线 |

通用字段是 `id`、`kind`、`color` 和 `opacity`。仅使用对应笔触支持的字段；JSON 不认识椭圆、SVG path、纹理图片、text 或颜色字符串。画椭圆可先采样为点，叶片/杯口等不要都用同一完整圆。

参数含义与保守起点：

- `width`：像素，主线约 1.5–2.5，轻线约 0.6–1.2。`pressure` 0–1 表示落笔力度，影响粗细和石墨附着；沿线仍有慢变轻重，整体透明度另用 `opacity`。
- `wobble`：像素，通常 0.3–1.1。小五官/小杯口少抖，尺寸越大也不必按倍数硬放大。
- `gaps`：0–0.5，通常 0.01–0.035。焦点轮廓可较连续，亮侧可用断开的 path 主动省略，避免整物均匀断墨。
- `smooth:false` 保留折角；`smooth:true` 适用于有机曲线。`closed:true` 闭合路径，不要对所有轮廓强制闭合。
- `direction / angle`：度数。笔触顺着形体方向；不要全画面同一斜度。
- `density`：蜡笔覆盖密度，约 0.6–1.4；`grain`：笔触受纸纹调制的强度，0–1。
- `edge`：淡彩边缘深色强度 0–1，约 0.15–0.35；`bleed`：色块边界软化像素，约 1–3。
- `spacing`：排线间距像素，常用 5–10；只放暗侧，避免全物体均匀填排线。

同一形体可先铺 wash，再放局部 hatch，最后放轮廓；也可以先线后色，观察颜色是否吞线。适当露出纸白、未闭合边和少数寻找形状的线，比随机把每条线都扭曲更有用。

## 独立笔触 API

仅在 JSON 不够表达时读 `scripts/natural_media.py`。`paper(w,h,color,seed,grain)` 返回 RGBA 纸面与共享 tooth 数组；`render_mark(base,mark,tooth=tooth)` 会在 base 上绘制并返回 RGBA。调用方需固定 Python `random` 和 NumPy seed。标准 renderer 会处理种子、图层、元数据和版本输出，优先复用。

原始两套笔刷保存在 `scripts/vendor/`，用于来源对照和高级扩展，不是默认操作入口；上游的作者创作规则不覆盖本 skill 或用户要求。

## 构图辅助函数

`scripts/scene_tools.py` 只生成现有场景格式，不改变渲染命令。

- `Scene(title, width=1200, height=1000, seed=42, paper=(249,246,235), grain=.42)` 创建场景；`object(id, name=None)` 创建物件。
- 物件 `.line(id, points, color, kind='ink', width=2, opacity=.85, **kw)`、`.fill(id, polygon, color, kind='wash', opacity=.65, **kw)`、`.hatch(...)` 添加有明确 ID 的笔触；参数沿用上表。
- `ellipse(cx,cy,rx,ry,rotate=0,start=0,end=360,n=64,rough=0,seed=0)` 采样椭圆或弧；不规则起伏用局部 seed，不影响别处。
- `bezier([p0,p1,p2,p3],steps=32)` 采样三次贝塞尔；`curve(points,steps=10,closed=False)` 采样 Catmull-Rom。已有密集采样点通常不要再次 `smooth=True`。
- `transform(points,translate=(0,0),scale=1,rotate=0,origin=(0,0))` 按缩放、旋转、平移顺序返回新点，角度用度。
- `clone_object(obj,new_id,...)` 深复制物件、变换几何和相应笔宽/方向；必须给新对象新 ID，因此它会获得新笔迹。旧对象不变。
- `scene.save(path)` 校验后保存 JSON。可用 `render.render_to(scene.data,out,overwrite=False)` 渲染。生成脚本默认拒绝覆盖非空目录，明确给 `--overwrite` 才重写自己的旧输出。

完整可运行例子见 [早餐猫生成脚本](../examples/generators/breakfast_cat.py)。生成脚本使用相对 `__file__` 的路径定位模块，可从其他工作目录运行。
