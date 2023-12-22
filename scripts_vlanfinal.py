from getpass import getpass
from netmiko import ConnectHandler
import re

def ssh_login(host, username, password, enable_password):
    device = {
        'device_type': 'cisco_ios',
        'ip': host,
        'username': username,
        'password': password,
        'secret': enable_password
    }

    try:
        ssh = ConnectHandler(**device)
        ssh.enable()  # Entra no modo privilegiado (enable)
        return ssh
    except Exception as e:
        print(f"Erro: {e}")
        return None

def extract_ports(output):
    ports = []
    lines = output.splitlines()
    start_capture = False
    for line in lines:
        if "Ports" in line:
            start_capture = True
        elif start_capture and line.strip():
            # Procura por qualquer padrão que contenha / ou Po (com números e letras)
            matches = re.findall(r"(\S+/\S+|Po\S+)", line)
            if matches:
                # Separa as portas, removendo espaços extras
                port_list = [p.strip() for match in matches for p in match.split(',') if p.strip()]
                ports.extend(port_list)
                
              

    return ports



def search_vlan_on_switch(switch_ip, switch_username, switch_password, switch_enable_password, vlans_to_search):
    # Log in to the switch
    ssh = ssh_login(switch_ip, switch_username, switch_password, switch_enable_password)

    if not ssh:
        print(f"Falha ao conectar ao switch {switch_ip}.")
        return

    try:
        # Criar um arquivo para armazenar todos os resultados
        with open(f"search_results_on_{switch_ip}.txt", "w") as results_file:
            for vlan_id_procurada in vlans_to_search:
                # Execute o comando para obter informações sobre a VLAN específica
                output = ssh.send_command(f"show vlan id {vlan_id_procurada}")

                # Extrair as portas da saída
                ports = extract_ports(output)

                # Adicionar os resultados ao arquivo
                results_file.write(f"Resultado para VLAN {vlan_id_procurada} no switch {switch_ip}:\n")
                for port in ports:
                    results_file.write(f"interface {port}\n")
                    results_file.write(f" switchport trunk allowed vlan remove {vlan_id_procurada}\n")
                results_file.write("\n")  # Adicionar uma linha em branco entre os resultados de VLANs diferentes

            print(f"Arquivo de resultados criado para o switch {switch_ip}: search_results_on_{switch_ip}.txt")

    except Exception as e:
        print(f"Erro: {e}")

    finally:
        # Fechar a conexão SSH
        ssh.disconnect()

def main():
    # Ler endereços IP dos switches de um arquivo
    with open("switch_ips.txt", "r") as ip_file:
        switch_ips = ip_file.read().splitlines()

    switch_username = input("Switch SSH Username: ")
    switch_password = input("Switch SSH Password: ")
    switch_enable_password = getpass("Switch Enable Password: ")

    # Ler VLANs a serem pesquisadas de um arquivo
    with open("vlans_to_search.txt", "r") as vlan_file:
        vlans_to_search = vlan_file.read().splitlines()

    # Iterar sobre cada endereço IP
    for switch_ip in switch_ips:
        print(f"\nProcurando VLANs nos switch {switch_ip}")
        search_vlan_on_switch(switch_ip, switch_username, switch_password, switch_enable_password, vlans_to_search)

if __name__ == "__main__":
    main()
