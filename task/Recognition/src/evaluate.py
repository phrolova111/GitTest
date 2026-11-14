"""加载 CIFAR-10 模型权重并评估测试集。"""
# 读取train.py产出的best.pt,在测试集上跑一遍，得出总体准确率和每类准确率

from __future__ import annotations

import argparse
from pathlib import Path    #面向对象路径

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import CIFAR10

from model import build_model


TASK_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = Path.home() / "data" / "cifar10"
DEFAULT_WEIGHTS = TASK_DIR / "weights" / "best.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a CIFAR-10 CNN checkpoint."
    )
    parser.add_argument(
        "--data-root",
        type=str,
        default=str(DEFAULT_DATA_ROOT),
        #default不走type切换，手动str切换
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=str(DEFAULT_WEIGHTS),
    )
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--samples", type=int, default=10)
    return parser.parse_args()


#构建测试集管道build_test_loader


def build_test_loader(
    data_root: Path,
    batch_size: int,
    num_workers: int,
    device: torch.device,
) -> tuple[CIFAR10, DataLoader]:
    test_transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.4914, 0.4822, 0.4465),
                std=(0.2470, 0.2435, 0.2616),
            ),
        ]
    )

    try:
        test_set = CIFAR10(
            root=str(data_root),
            train=False,
            transform=test_transform,
            download=False,
        )
    except RuntimeError as error:
        raise RuntimeError(
            f"无法读取 CIFAR-10 测试集，请检查目录：{data_root}"
        ) from error

    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=device.type == "cuda",
    )
    return test_set, test_loader


def main() -> None:
    args = parse_args()

    data_root = Path(args.data_root).expanduser()
    weights_path = Path(args.weights).expanduser()

    if not weights_path.is_file():
        raise FileNotFoundError(
            f"找不到模型权重：{weights_path}\n"
            "请先运行 train.py，或使用 --weights 指定正确路径。"
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_set, test_loader = build_test_loader(
        data_root=data_root,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        device=device,
    )

    # 必须重新创建与训练时结构相同的模型。
    model = build_model(num_classes=10).to(device)

    try:
        state_dict = torch.load(
            weights_path,
            map_location=device,
            weights_only=True,
        )
        model.load_state_dict(state_dict)
    except Exception as error:
        raise RuntimeError(
            f"加载模型权重失败：{weights_path}"
        ) from error

    model.eval()

    criterion = nn.CrossEntropyLoss()
    class_names = test_set.classes
    number_of_classes = len(class_names)

    class_correct = [0] * number_of_classes
    class_total = [0] * number_of_classes

    total_samples = 0
    correct_predictions = 0
    total_loss = 0.0
    printed_samples = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            predictions = outputs.argmax(dim=1)

            total_loss += loss.item() * images.size(0)
            total_samples += labels.size(0)
            labels_cpu = labels.cpu()
            predictions_cpu = predictions.cpu()

            correct_predictions += (
                predictions_cpu == labels_cpu
            ).sum().item()

            for true_label, predicted_label in zip(
                labels_cpu,
                predictions_cpu,
            ):
                class_total[true_label.item()] += 1

                if true_label.item() == predicted_label.item():
                    class_correct[true_label.item()] += 1

            # 只输出前面若干张图片的真实和预测类别。
            for true_label, predicted_label in zip(
                labels_cpu,
                predictions_cpu,
            ):
                if printed_samples >= args.samples:
                    break

                print(
                    f"true={class_names[true_label.item()]}, "
                    f"predicted={class_names[predicted_label.item()]}"
                )
                printed_samples += 1

    accuracy = correct_predictions / total_samples
    average_loss = total_loss / total_samples

    # 输出设备，权重，样本数，正确数，总准确率，平均loss
    print("\nTest results")
    print(f"Device: {device}")
    print(f"Weights: {weights_path}")
    print(f"Total samples: {total_samples}")
    print(f"Correct: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Loss: {average_loss:.4f}")

    print("\nAccuracy by class:")
    for class_index, class_name in enumerate(class_names):
        if class_total[class_index] == 0:
            class_accuracy = 0.0
        else:
            class_accuracy = (
                class_correct[class_index]
                / class_total[class_index]
            )

        print(
            f"{class_name}: "
            f"{class_correct[class_index]}/"
            f"{class_total[class_index]} "
            f"({class_accuracy:.2%})"
        )


if __name__ == "__main__":
    main()