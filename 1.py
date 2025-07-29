import pandas as pd
import numpy as np

def clean_excel_data_exact(input_file_path, output_file_path=None):
    try:
        # 1. 读取整个Excel文件的前10列，不设置任何行作为header
        df_full = pd.read_excel(input_file_path, header=None, usecols=range(10))

        # df_fixed_rows 包含第1到第8行（DataFrame索引0到7）
        df_fixed_rows = df_full.iloc[:8].copy()
        # df_data_to_filter 包含从第9行开始的数据（DataFrame索引8及以后）
        df_data_to_filter = df_full.iloc[8:].copy()

        print(f"待处理的数据部分包含 {df_data_to_filter.shape[0]} 行。")

        # 4. 筛选逻辑：针对第9列（Excel的I列，DataFrame的第9列，索引为8）进行非空判断
        col_index_to_filter = 8 # 第9列在DataFrame中的索引是8 (0-indexed)

        if df_data_to_filter.shape[1] <= col_index_to_filter:
            raise ValueError(f"数据列数不足{col_index_to_filter + 1}列，无法找到第{col_index_to_filter + 1}列进行筛选。")

        # 将筛选列中所有只包含空格的字符串转换为空值 (NaN)
        # 注意：这里我们使用默认的数字列名进行操作
        if df_data_to_filter[col_index_to_filter].dtype == 'object':
            df_data_to_filter[col_index_to_filter] = df_data_to_filter[col_index_to_filter].replace(r'^\s*$', np.nan, regex=True)

        # 5. 筛选数据：只保留第9列不为空的行
        df_data_cleaned = df_data_to_filter[df_data_to_filter[col_index_to_filter].notna()]
        print(f"数据部分筛选后，剩余 {df_data_cleaned.shape[0]} 行。")

        # 6. 拼接保留的行和筛选后的数据行
        # 因为我们读取时没有设置header，所以df_fixed_rows和df_data_cleaned的列名都是数字索引，可以直接拼接
        df_final = pd.concat([df_fixed_rows, df_data_cleaned], ignore_index=False)
        print(f"最终合并后的数据包含 {df_final.shape[0]} 行, {df_final.shape[1]} 列。")

        # 7. 如果指定了输出文件路径，则保存最终数据
        if output_file_path:
            # 实际保存文件的代码：将 df_final 写入 Excel 文件
            df_final.to_excel(output_file_path, index=False, header=False) # header=False 避免DataFrame的数字列名写入文件
            print(f"清理并合并后的数据已保存到: {output_file_path}")

        return df_final

    except FileNotFoundError:
        print(f"错误：文件未找到，请检查路径是否正确: {input_file_path}")
        return None
    except ValueError as ve:
        print(f"数据处理错误: {ve}")
        return None
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return None

input_excel_path = '蒋柳青-数据图谱(电流版).xlsx'
output_excel_path = '1.xlsx'

# 执行清理操作
cleaned_and_preserved_df = clean_excel_data_exact(input_excel_path, output_excel_path)