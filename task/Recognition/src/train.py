"""训练 CIFAR-10 CNN 并保存模型权重。"""

from __future__ import annotations

import argparse            #导入argparse模块，解析命令行参数
import random              #导入random模块，设置随机种子
import time
from pathlib import Path   #导入Path模块，处理文件路径，面向对象的路径操作

import torch
from torch import nn
#从torch里导入nn子模块(神经网络模块)
# 后面用nn.Linear、nn.CrossEntropyLoss都通过nn访问
from torch.utils.data import DataLoader
#数据加载器。将数据集切成一个个batch，方便训练
from torchvision import transforms
#图像增强模块。后面用transforms.Compose、transforms.RandomCrop等都通过transforms访问
from torchvision.datasets import CIFAR10
#内置的CIFAR-10数据集类。后面用CIFAR10(root, train, transform, download)创建训练集和测试集

from model import build_model
#从同目录的 model.py 导入 build_model 函数，方便以后替换模型结构只需要改model.py


TASK_DIR = Path(__file__).resolve().parents[1]       
#__file__ 是当前脚本的文件路径
# .resolve() 转成绝对路径，并解析符号链接
# .parents[1] 获取上上级目录，即项目根目录，这样权重路径就不依赖从哪个目录运行脚本
DEFAULT_DATA_ROOT = Path.home() / "data" / "cifar10"   
#返回当前用户主目录，默认把数据放在 ~/data/cifar10，避免污染项目目录
DEFAULT_WEIGHTS_DIR = TASK_DIR / "weights"
#默认权重输出到任务根目录/weights，避免污染项目目录


#函数 1：parse_args —— 解析命令行参数

def parse_args() -> argparse.Namespace:
#argparse.Namespace 是"返回类型注解"，
#说明这个函数返回一个 Namespace 对象(就是存参数的小容器)
    parser = argparse.ArgumentParser(description="Train a CNN on CIFAR-10.")
    parser.add_argument(
        "--data-root",
        type=str,
        default=str(DEFAULT_DATA_ROOT),
        help="CIFAR-10 dataset directory.",
    )
    parser.add_argument(
        "--weights-dir",
        type=str,
        default=str(DEFAULT_WEIGHTS_DIR),
        help="Directory used to save model weights.",
    )
    parser.add_argument("--epochs", type=int, default=10)
    #将整个训练集完整过10遍
    parser.add_argument("--batch-size", type=int, default=64)
    #每次给模型喂64张图，太小训练不稳，太大显存/内存吃不消
    parser.add_argument("--learning-rate", type=float, default=0.001)
    #学习率 = 每次参数更新的步长。太大震荡、太小学得慢
    parser.add_argument("--num-workers", type=int, default=2)
     # 0 = 主进程加载(简单但慢)；2 = 两个子进程并行预取，缓解"等数据"
    parser.add_argument("--seed", type=int, default=42)
    #随机种子，固定他，大致复现结果
    return parser.parse_args()
    #parse_args() 真正去读命令行，返回一个Namespace对象。
    #之后用args.epochs、args.batch_size访问。


# 函数 2：set_seed —— 固定随机种子


def set_seed(seed: int) -> None:     #参数类型为整数，无返回值
    random.seed(seed)
    torch.manual_seed(seed)
    # 固定 PyTorch 在 CPU 上的随机种子。
    # 影响：权重初始化、Dropout 掩码、torch 层的随机增强

    if torch.cuda.is_available():   #判断有没有可用的GPU
        torch.cuda.manual_seed_all(seed)   #固定所有GPU的随机种子


# 函数 3：build_dataloaders —— 构建数据管道


def build_dataloaders(
    data_root: Path,
    batch_size: int,
    num_workers: int,
    device: torch.device,
) -> tuple[DataLoader, DataLoader]:
    # 训练集使用随机裁剪和翻转，降低过拟合。
    train_transform = transforms.Compose(
        [
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.4914, 0.4822, 0.4465),
                std=(0.2470, 0.2435, 0.2616),
            ),
        ]
    )

    # 测试集只使用确定性的预处理，不能随机增强。
    test_transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.4914, 0.4822, 0.4465),
                std=(0.2470, 0.2435, 0.2616),
            ),
        ]
    )

    #创建数据集对象
    train_set = CIFAR10(
        root=str(data_root),   #数据集存放路径
        train=True,   #表示训练集5000张图
        transform=train_transform,
        download=True,
    )
    test_set = CIFAR10(
        root=str(data_root),
        train=False,  #表示测试集10000张图
        transform=test_transform,
        download=True,
    )

    # DataLoader 是 PyTorch 的数据加载器，负责将数据集切分成一个个 batch，并在训练时按需加载。
    train_loader = DataLoader(
        train_set,
        batch_size=batch_size,   #每个 batch 的样本数
        shuffle=True,
        #打乱，CIFAR 数据集是按类别顺序排列的，如果每个 batch 都是"全是猫"或"全是狗"，模型会学到错误规律，而且类别分布有偏，训练不稳定。
        num_workers=num_workers,    #加载数据的子进程数。0 = 主进程加载(简单但慢)；2 = 两个子进程并行预取，缓解"等数据"
        pin_memory=device.type == "cuda",
    )
    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=False,
        #不打乱，测试集需要保证结果的可复现性，对准确性无影响
        num_workers=num_workers,
        pin_memory=device.type == "cuda",
    )

    return train_loader, test_loader


# 函数 4：evaluate  评估
#   1. model.eval()      关 Dropout、BN 用 running 统计
#   2. with torch.no_grad()  不建计算图，省显存、加速
#   3. 按样本数加权平均   处理最后一个不满 batch


def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()   #切换到评估模式，关闭Dropout和BN的训练行为
    total_loss = 0.0
    #累加总的loss，后面除以总样本数得到平均loss
    correct = 0
    #累加预测正确的样本数
    total = 0
    # 累加见过的样本数

    with torch.no_grad():
        for images, labels in dataloader:
            #DataLoader 是"可迭代对象"，每次迭代返回 (images, labels)：
            #images: (batch_size, 3, 32, 32) 的张量
            #labels: (batch_size,) 的张量，每个是 0~9 的整数
            images = images.to(device)
            #把张量搬到指定设备
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            #loss.item() 把"只有一个元素的张量"转成 Python float
            #loss.item() 是这个 batch 的"平均 loss"
            #乘以 images.size(0)(=batch 大小)还原成"这个 batch 的总 loss"
            #为什么要这样：最后一个 batch 可能不满，直接平均 batch loss 会有偏差
            #按样本数加权平均才是精确的全数据集均值
            predictions = outputs.argmax(dim=1)
            #argmax(dim=1) 沿"类别维"找最大值的位置，即预测的类别。
            #例：outputs[i] = [0.1, 0.7, 0.2]，argmax 返回 1。

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / total   #全数据平均loss
    accuracy = correct / total          #全数据集准确率
    return average_loss, accuracy


# 函数 5：train_one_epoch —— 训练一轮
# zero_grad → forward → loss → backward → step


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> tuple[float, float]:
    model.train()
    #切换到训练模式
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        #shuffle=True 让每轮顺序不同
        images = images.to(device)
        labels = labels.to(device)

        # 一次训练迭代的固定顺序。
        optimizer.zero_grad()
        #清空梯度缓存，避免梯度累加
        outputs = model(images)
        loss = criterion(outputs, labels)   #算损失
        loss.backward()    #反向传播，从loss出发，沿着计算图自动求每个参数的梯度
        optimizer.step()   #更新参数，沿着梯度下降一步

        total_loss += loss.item() * images.size(0)
        predictions = outputs.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    average_loss = total_loss / total   #全数据集平均loss
    accuracy = correct / total          #全数据集准确率
    return average_loss, accuracy


# 函数 6：main


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    data_root = Path(args.data_root).expanduser()
    weights_dir = Path(args.weights_dir).expanduser()
    weights_dir.mkdir(parents=True, exist_ok=True)
    #先创建目录，让torch.save找到路径

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #三目运算：有 GPU 用 cuda，否则 cpu

    print(f"Device: {device}")
    print(f"Data root: {data_root}")
    print(f"Weights directory: {weights_dir}")
    print(
        f"Epochs: {args.epochs}, "
        f"batch size: {args.batch_size}, "
        f"learning rate: {args.learning_rate}"
    )
    #打印配置，回看best.pt就能知道权重是用什么超参调出来的

    train_loader, test_loader = build_dataloaders(
        data_root=data_root,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        device=device,
    )

    model = build_model(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    #build_model 是唯一与网络定义接触的地方。
    #.to(device) 把模型所有参数搬到目标设备
    optimizer = torch.optim.Adam(
        #Adam优化器：自适应学习率，收敛快，对lr不敏感，适合快速baseline
        model.parameters(),
        #model.parameters() 遍历模型所有"需要训练的参数"
        #包括卷积权重、BN 的 γ/β、全连接权重
        #优化器拿到这个列表后，step() 时逐个更新
        lr=args.learning_rate,
    )

    best_accuracy = -1.0
    #用-1初始化。准确率不为负，保证第一个epoch一定刷新最佳
    #如果用0初始化，万一第一轮准确率就是 0(理论上)，就不会保存了
    training_start = time.time()

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()

        train_loss, train_accuracy = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )
        #train_one_epoch 内部会 model.train()，会更新参数
        test_loss, test_accuracy = evaluate(
            model=model,
            dataloader=test_loader,
            criterion=criterion,
            device=device,
        )
        #evaluate 内部会 model.eval()，不更新参数
        #先train后evaluate，保证每轮都用最新参数评估

        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            torch.save(model.state_dict(), weights_dir / "best.pt")
            print(f"Saved new best model: {test_accuracy:.2%}")
            #大于时保存最佳模型参数，便于后续利用
            #只保存state_dict()，文件更小，加载时不依赖在哪个文件，更加安全

        #同时保存最后一轮参数，便于排查训练过程。
        #每轮都覆盖最后一轮参数，训练崩了可以查最后一轮、断点续训、对比 best 和 last
        torch.save(model.state_dict(), weights_dir / "last.pt")

        elapsed = time.time() - epoch_start
        print(
            f"Epoch {epoch:02d}/{args.epochs:02d} | "
            f"train loss={train_loss:.4f} | "
            f"train acc={train_accuracy:.2%} | "
            f"test loss={test_loss:.4f} | "
            f"test acc={test_accuracy:.2%} | "
            f"time={elapsed:.1f}s"
        )
        #train和test并排打印：
        #train高test低 过拟合
        #train低test低 欠拟合
        #都高          训练良好 

    total_time = time.time() - training_start
    print(f"Best test accuracy: {best_accuracy:.2%}")
    print(f"Total training time: {total_time:.1f}s")
    print(f"Best weights: {weights_dir / 'best.pt'}")
    #打印出训练结束后的最佳测试准确率、总训练时间和最佳权重文件路径


if __name__ == "__main__":
    main()