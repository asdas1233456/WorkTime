import json
from pathlib import Path
from report_overtime import report_overtime
from advisor import make_plan
from paths import CONFIG_PATH, OUTPUT_DIR


def select_input_file():
    """让用户选择输入的Excel文件，单个文件时自动选中"""
    # 根目录（config.json所在目录）
    root_dir = CONFIG_PATH.parent
    # 获取所有Excel文件
    excel_files = list(root_dir.glob("*.xlsx")) + list(root_dir.glob("*.xls"))

    # 情况1：没有找到Excel文件
    if not excel_files:
        print("未在根目录检测到Excel文件（.xlsx/.xls）")
        # 让用户手动输入路径
        file_path = input("请输入Excel文件路径（绝对路径或相对根目录的路径）：").strip()
        file = Path(file_path)
        if not file.is_absolute():
            file = root_dir / file
        if file.exists() and file.suffix in ['.xlsx', '.xls']:
            return file
        else:
            raise FileNotFoundError(f"文件不存在或不是Excel文件：{file}")

    # 情况2：只有一个Excel文件，自动选中
    elif len(excel_files) == 1:
        selected_file = excel_files[0]
        print(f"检测到唯一Excel文件：{selected_file.name}，将自动使用该文件")
        return selected_file

    # 情况3：多个Excel文件，让用户选择
    else:
        print("检测到根目录下的Excel文件：")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file.name}")

        # 循环直到用户输入有效序号
        while True:
            choice = input("\n请输入文件序号（1-{}）：".format(len(excel_files))).strip()
            if choice.isdigit() and 1 <= int(choice) <= len(excel_files):
                return excel_files[int(choice) - 1]
            else:
                print(f"请输入有效的序号（1到{len(excel_files)}之间）")


def main():
    try:
        # 1) 选择输入文件（自动处理单个文件的情况）
        input_file = select_input_file()
        print(f"已选择文件：{input_file.name}")

        # 2) 读配置
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)

        # 3) 生成计划
        df = report_overtime(input_file, CONFIG_PATH)
        summary_df, advice, json_result = make_plan(df, cfg)

        # 4) 落盘
        summary_df.to_excel(OUTPUT_DIR / "加班计划.xlsx", index=False)
        with open(OUTPUT_DIR / "加班计划.txt", "w", encoding="utf-8") as f:
            f.write(advice)
        with open(OUTPUT_DIR / "加班计划.json", "w", encoding="utf-8") as f:
            json.dump(json_result, f, ensure_ascii=False, indent=2)

        print(f"\n已生成文件到 {OUTPUT_DIR} 目录：")
        print("- 加班计划.xlsx")
        print("- 加班计划.txt")
        print("- 加班计划.json")
    except FileNotFoundError as e:
        print(f"错误：找不到文件 - {str(e)}")
        print("请确保：")
        print(f"- 根目录下有配置文件 'config.json'")
        print(f"- 输入的Excel文件路径正确")
    except Exception as e:
        print(f"执行失败：{str(e)}")


if __name__ == "__main__":
    main()
