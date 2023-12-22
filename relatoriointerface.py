def consolidate_interfaces(input_file, output_file):
    interface_dict = {}

    # Ler o arquivo de resultados
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Processar linhas do arquivo
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith("interface"):
            interface = line.split()[1]
            vlan_line = lines[i + 1].strip()
            vlan_id = vlan_line.split()[-1]

            # Verificar se a interface já está no dicionário
            if interface in interface_dict:
                interface_dict[interface].append(vlan_id)
            else:
                interface_dict[interface] = [vlan_id]

    # Criar um novo arquivo consolidado
    with open(output_file, "w") as output:
        for interface, vlans in interface_dict.items():
            output.write(f"interface {interface}\n")
            output.write(f" switchport trunk allowed vlan {','.join(vlans)}\n\n")

    print(f"Arquivo consolidado criado: {output_file}")

def main():
    input_file = input("Digite o nome do arquivo de resultados: ")
    output_file = input("Digite o nome do arquivo consolidado: ")

    consolidate_interfaces(input_file, output_file)

if __name__ == "__main__":
    main()
