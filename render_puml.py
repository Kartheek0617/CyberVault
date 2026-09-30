import glob
import os
from plantuml import PlantUML

def main():
    pl = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    input_dir = 'docs/diagrams/'
    output_dir = 'docs/evidence/diagrams/'
    
    os.makedirs(output_dir, exist_ok=True)
    
    puml_files = glob.glob(os.path.join(input_dir, '*.puml'))
    
    for puml_file in puml_files:
        filename = os.path.basename(puml_file)
        name, _ = os.path.splitext(filename)
        output_file = os.path.join(output_dir, f"{name}.png")
        
        print(f"Processing {puml_file} -> {output_file}")
        try:
            pl.processes_file(puml_file, outfile=output_file)
            print(f"Successfully generated {output_file}")
        except Exception as e:
            print(f"Error processing {puml_file}: {e}")

if __name__ == '__main__':
    main()
