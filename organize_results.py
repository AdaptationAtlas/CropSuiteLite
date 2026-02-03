import yaml
import os
import sys
import shutil
from pathlib import Path

def split_modelscenarios(fld_name):
    if 'ssp' in fld_name:
        ssppos = fld_name.index('ssp')

        scenario = fld_name[ssppos:ssppos+6]
        model = fld_name[:ssppos-1]
        period = fld_name[ssppos+7:ssppos+16]
    else:
        histpos = fld_name.index('historical')
        scenario = 'historical'
        model = fld_name[:histpos-1]
        period = fld_name[histpos+11:histpos+20]
    return scenario, model, period

def find_folder_largest_files(filepaths, filetocompare):
    sizes = []
    for fn in filepaths:
        file_path = Path(fn) / filetocompare
        if not file_path.exists(): sizes.append(0)
        
        sizes.append(file_path.stat().st_size)
    sizes_max = max(sizes)
    return filepaths[sizes.index(sizes_max)]

def main(config):

    with open(config, 'r') as file:
        config = yaml.safe_load(file)

    response_path = config['SOLUTIONS']['solutions_path']
    use_product = config['SOLUTIONS'].get('product_output', False)
    print('----------------> Use Product instead of minimun: ', use_product)
    input_path = config['GENERAL']['output_path']
    if os.path.basename(input_path) == '': input_path = input_path[:-1]
    
    output_dir = input_path + '_summary'
    if not os.path.exists(output_dir): os.mkdir(output_dir)

    with open(response_path, 'r') as file:
        response_dict = yaml.safe_load(file)

    folder_withresults = [os.path.join(input_path, i) for i in os.listdir(input_path) if i.endswith('novar')]

    for fld in folder_withresults:

        ## list of files in the folder
        listfolders = [os.path.join(fld,i) for i in os.listdir(fld) if os.path.isdir(os.path.join(fld,i))]
        if len(listfolders)>1:
            fld_all = find_folder_largest_files(listfolders, 'slope_combined.tif')
        else:
            fld_all = listfolders[0]

        print(f'********* Main results from folder {fld_all} will be copied')
        if not os.path.exists(fld_all): continue
        scenario, model, period = split_modelscenarios(os.path.split(fld)[-1])
        
        mname = model.replace('-','_')
        
        fld_layers = [i for i in os.listdir(fld_all) if os.path.isdir(os.path.join(fld_all,i))]

        for specific_run in fld_layers:
            if use_product:
                cs_path = os.path.join(fld_all, specific_run, 'crop_suitability_multi.tif')
            else:
                cs_path = os.path.join(fld_all, specific_run, 'crop_suitability.tif')
            
            if not specific_run.startswith('ST'):
                solution_st, crop_n, sol_code = 'ST0', specific_run, 'bl'
            else:
                solution_st, sol_code, crop, _, _ = specific_run.split('_')
                crop_n = response_dict['CROPS'][crop].lower()

            newname = f'{solution_st}_{mname}_{scenario}_{period}_{crop_n}_{sol_code}_suit.tif'
            if os.path.exists(os.path.join(output_dir, newname)): continue
            print(cs_path, newname)
            shutil.copy(cs_path, os.path.join(output_dir, newname))
                


if __name__ == '__main__':
    args = sys.argv[1:]
    config = args[args.index("-config") + 1] if "-config" in args and len(args) > args.index("-config") + 1 else None
    print(config)    
    main(config)
