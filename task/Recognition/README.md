# 目标识别任务

![CNN 图像分类流程示意图](../../assets/tasks/recognition-cnn-v2.png)

*任务流程示意图，非实际运行结果。*

使用 **Python + PyTorch** 实现并训练一个 CNN 模型，完成图像分类。

## CNN 简介

CNN（Convolutional Neural Network，卷积神经网络）是一类适合处理图像的神经网络。它通过训练学习图像中的特征，例如边缘、纹理和形状，再根据这些特征判断图像类别。

常见的 CNN 分类模型包含以下部分：

- **卷积层**：用可学习的卷积核扫描图像的局部区域，提取特征；同一个卷积核在不同位置共享参数。
- **激活函数**：如 ReLU，引入非线性，使网络能够学习更复杂的特征。
- **池化层**：对局部特征进行汇总，缩小特征图尺寸，减少后续计算量。
- **分类层**：综合提取到的特征，为每个类别输出一个分数，选择分数最高的类别作为预测结果。

在本任务中，输入是一张 CIFAR-10 图像，输出是 10 个类别的分数。训练时，用损失函数衡量预测与真实标签的差异，通过反向传播计算梯度，再由优化器更新网络参数；推理时，使用训练好的参数预测图像类别。

## 数据集

使用 [CIFAR-10](https://www.cs.toronto.edu/~kriz/cifar.html)，通过 `torchvision.datasets.CIFAR10` 自动下载和加载。

## 实现要求

- 使用 PyTorch 定义 CNN 模型并编写训练代码。
- 使用 CIFAR-10 的 10 个类别完成分类，训练集用于训练，测试集只用于评估。
- 训练结束后将模型权重保存为 `.pt` 或 `.pth` 文件；评估程序须能重新创建模型、加载该权重并完成推理。
- 评估时输出测试集总样本数、正确分类数和总体准确率，并输出每个类别的准确率。准确率按实际运行结果报告，不预设统一门槛；README 中说明训练轮数、运行设备（CPU 或 GPU）及对应结果。
- 对若干测试集图像输出真实类别和模型预测类别，便于确认程序实际执行了分类推理，而不只是完成训练或保存权重。

## 代码与目录规范

- 代码放在 `task/Recognition/src/`，合理区分模型、训练和评估；任务根目录提供 `test.sh` 和 README。
- 关键步骤有必要注释，数据和权重路径、训练参数便于调整，加载失败时给出明确提示。
- 说明模型结构和数据处理方法，引用代码或模型时注明来源。

## 运行与验收

提供 `test.sh`，从仓库任务目录执行：

```bash
bash test.sh
```

脚本应运行训练和测试评估；评估须加载刚保存的权重。也可以提供独立评估命令，方便在已有权重时重复验证。一次有效的验收运行应能观察到：

1. 训练过程正常结束，并在指定位置生成非空的 `.pt` 或 `.pth` 权重文件。
2. 测试评估成功加载该权重，在 CIFAR-10 测试集上完成推理，并打印总样本数、正确数、总体准确率和各类别准确率。
3. 输出若干样本的真实类别与预测类别，例如 `true=cat, predicted=cat`；预测不必全部正确，README 如实记录运行结果。

## 提交要求

- 提交源码、依赖说明、`test.sh`、任务 README 和实际模型权重；权重通过可访问的下载链接提供。
- README 写明环境、训练与评估命令及执行目录、权重使用方法，以及实际设备、训练轮数、评估结果和未完成项。
- 用 `.gitignore` 排除数据集、权重、虚拟环境和缓存。Git 提交说明具体改动，提交前按 README 检查权重加载与评估能否复现。
- 提交时提供姓名或昵称、仓库链接、分支、提交号和权重链接，验收以该版本为准。

环境配置见[环境准备](../../ENV_SETUP.md)，神经网络与 PyTorch 教程见[学习资料与路径](../../LEARNING_RESOURCES.md)。

[返回培训考核首页](../../README.md)






## 实现与运行说明

### 环境依赖

- Ubuntu 22.04
- Python 3.10.12
- PyTorch 2.14.1+cpu
- torchvision 0.29.2+cpu
- 训练设备：CPU

依赖安装：

```bash
python -m pip install torch==2.14.1 torchvision==0.29.2 \
  --index-url https://download.pytorch.org/whl/cpu
```

### 实现思路

使用 PyTorch 自定义 CNN，对 CIFAR-10 数据集进行 10 类图像分类。

CIFAR-10 包含：

- 50000 张训练图片
- 10000 张测试图片
- 图片尺寸为 32×32 RGB

模型包含三个卷积阶段，特征图尺寸依次为：

```text
3×32×32 → 32×16×16 → 64×8×8 → 128×4×4
```

随后展平为 2048 维特征，经过全连接层输出 10 个类别分数。

训练集使用随机裁剪、随机水平翻转和归一化。测试集只使用归一化，不使用随机增强。

训练参数：

- 训练轮数：10
- batch size：64
- 学习率：0.001
- 损失函数：CrossEntropyLoss
- 优化器：Adam


### 训练

执行目录：

```bash
cd task/Recognition
```

训练命令：

```bash
python src/train.py --epochs 10
```

权重保存位置：

```text
weights/best.pt
weights/last.pt
```

### 评估

```bash
python src/evaluate.py --weights weights/best.pt
```

评估程序会重新创建模型，加载`best.pt`，并在完整测试集上计算总体准确率和各个分类的准确率


### 测试

```bash
cd task/Recognition
bash test.sh
```

### 实际测试结果

- 测试集总样本数：10000
- 正确分类数：8214
- 总体准确率：82.14%
- 测试损失：0.5290
- 最佳结果出现在第 9 轮
- 训练总时间：888.7 秒，约 14 分 49 秒

分类准确率：

```text
airplane:   799/1000 (79.90%)
automobile: 946/1000 (94.60%)
bird:       658/1000 (65.80%)
cat:        717/1000 (71.70%)
deer:       857/1000 (85.70%)
dog:        701/1000 (70.10%)
frog:       841/1000 (84.10%)
horse:      884/1000 (88.40%)
ship:       911/1000 (91.10%)
truck:      900/1000 (90.00%)
```

预测示例：

```text
true=cat, predicted=cat
true=ship, predicted=ship
true=ship, predicted=automobile
true=airplane, predicted=ship
true=frog, predicted=frog
true=frog, predicted=frog
true=automobile, predicted=automobile
true=frog, predicted=frog
true=cat, predicted=cat
true=automobile, predicted=automobile
```

### 模型权重
```text
https://github.com/phrolova111/GitTest/releases/download/recognition-v1/best.pt
```


### 参考资料

- PyTorch 基础教程：https://docs.pytorch.org/tutorials/beginner/basics/intro.html
- PyTorch CIFAR-10 教程：https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
- 《动手学深度学习》CNN：https://zh.d2l.ai/chapter_convolutional-neural-networks/index.html
- CIFAR-10 数据集：https://www.cs.toronto.edu/~kriz/cifar.html


### 未完成项

无
