import os, glob, subprocess, time
import pandas as pd

def run_daycent(scenario='temp', outvars_fn='preRUN_outvars.txt'):
    if os.path.isfile(scenario + ".bin"):
        os.remove(scenario + ".bin")
    comline = 'DDcentEVI.exe -s {} -n {}'.format(scenario, scenario)            
    run_model = subprocess.Popen(comline, cwd=".", stdout=subprocess.DEVNULL)
    run_model.wait()
    comline2 = 'DDlist100.exe {} {} {}'.format(scenario, scenario, outvars_fn)
    extract_model = subprocess.Popen(comline2, cwd=".", stdout=subprocess.DEVNULL)
    extract_model.wait()

def create_temp_scenario(sch_file):
    with open(sch_file, mode='r') as reader:
        lines = reader.readlines()
    blocks_n = len([line for line in lines if 'Block' in line])
    blocks_cnt = 0
    with open('temp.sch', mode='w') as writer:
        for line in lines:
            if 'Starting year' in line:
                year_st = line.split(' ')[0]
                writer.write(line)
            elif 'Last year' in line:
                if (blocks_cnt == blocks_n) or (blocks_cnt == 0):
                    year_en = line.split(' ')[0]
                    line = line.replace(year_en, str(int(year_st) + 10))
                    writer.write(line)
                else:
                    writer.write(line)
                blocks_cnt += 1
            else:
                writer.write(line)

def init_site_wPreRun(scenario, df):        
    site_file = scenario + '.100'    
    idxs_somiv = {
        'SOM1CI(1,1)': df['som1c(1)'].iloc[0],         
        'SOM2CI(1,1)': df['som2c(1)'].iloc[0],
        'CLITTR(1,1)': df['clittr(1,1)'].iloc[0],
        'CLITTR(2,1)': df['clittr(2,1)'].iloc[0],
        'MINERL(1,1)': df['minerl(1,1)'].iloc[0],
        'MINERL(2,1)': df['minerl(2,1)'].iloc[0],
        'MINERL(3,1)': df['minerl(3,1)'].iloc[0],
        'MINERL(4,1)': df['minerl(4,1)'].iloc[0],
        'MINERL(5,1)': df['minerl(5,1)'].iloc[0],
        'MINERL(6,1)': df['minerl(6,1)'].iloc[0],
        'MINERL(7,1)': df['minerl(7,1)'].iloc[0],
        'MINERL(8,1)': df['minerl(8,1)'].iloc[0],
        'MINERL(9,1)': df['minerl(9,1)'].iloc[0],
        'MINERL(10,1)': df['minerl(10,1)'].iloc[0],
        'RWCF(1)': df['rwcf(1)'].iloc[0],
        'RWCF(2)': df['rwcf(2)'].iloc[0],
        'RWCF(3)': df['rwcf(3)'].iloc[0],
        'RWCF(4)': df['rwcf(4)'].iloc[0],
        'RWCF(5)': df['rwcf(5)'].iloc[0],
        'RWCF(6)': df['rwcf(6)'].iloc[0],
        'RWCF(7)': df['rwcf(7)'].iloc[0],
        'RWCF(8)': df['rwcf(8)'].iloc[0],
        'RWCF(9)': df['rwcf(9)'].iloc[0]
    }
    with open(site_file, 'r') as file:
            lines = file.readlines()        
    updated_lines = [
        f"{idxs_somiv.get(line.split()[1].strip(), float(line.split()[0])):<17.4f} {line.split()[1]}\n"
        if line.split()[1].strip() in idxs_somiv else line
        for line in lines
    ]
    with open(site_file, 'w') as file:
            file.writelines(updated_lines)
    return 0  

def main(sites_path):
    sites = [subdir for subdir, dirs, files in os.walk(sites_path)][1:]
    for site in sites:
        os.chdir(site)
        sch_files = [sch for sch in glob.glob(os.path.join(site, "*.sch"))]
        for sch_file in sch_files:
            scenario = os.path.basename(os.path.normpath(sch_file)).replace('.sch', '')
            print(scenario)
            create_temp_scenario(sch_file)
            run_daycent()
            time.sleep(2)
            df0 = pd.read_csv('temp.lis', sep=r'\s+', skiprows=1)   
            lis_df = df0.iloc[-1:]
            init_site_wPreRun(scenario, lis_df)
            for temp_file in [
                'temp.lis',
                'temp.sch',
                'temp.bin'
            ]:
                os.remove(temp_file)

sites_path = r"C:\comet-farm-daycent-model-source-code-main\Test with exp sites\mt\multi_main"
main(sites_path)
