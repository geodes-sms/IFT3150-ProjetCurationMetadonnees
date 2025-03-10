from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for a IFT3710 for the final presentation of IFT 3150 at UdeM


class IFT3710(SRProject):
    """
    Digital-twin-based testing for cyber–physical systems: A systematic literature review
    https://www.sciencedirect.com/science/article/pii/S0950584922002543
    Size: 454
    Included: 147
    Excluded: 307
    Inclusion rate: 32%%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Full-text decision available
    """

    def __init__(self):
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/IFT3710/IFT3710-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="projects")  # 458 rows
            print(sheet_all)
        

        # Add columns
        self.df['title'] = sheet_all["Title"]
        self.df['link'] = sheet_all["Link"]
        self.df['doi'] = self.df['link']

        self.df['project'] = "IFT3710"
        self.export_path = f"{MAIN_PATH}/Datasets/IFT3710/IFT3710.tsv"
        print(self.df)


if __name__ == '__main__':
    IFT3710 = IFT3710()
    IFT3710.df.to_csv(IFT3710.export_path, sep='\t')
