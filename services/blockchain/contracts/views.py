from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from web3 import Web3
# from dotenv import load_dotenv

# # Cargar variables de entorno desde un archivo .env (si lo tienes)
# load_dotenv()

# Tu endpoint de Infura para Sepolia (asegúrate de que sea el correcto)
#print in RED:
print("\033[91m" + "INICIANDOOOOOO BLOCKCHAIN!!!!!!!!!!!!!!!!!!!!!!!!!!dd!!!!s!!!!!!!!!!!asd!!!!" + "\033[0m")
sepolia_node_url = "https://sepolia.infura.io/v3/e9bce358a6aa4324bc1f53e803b54662"
print(f"Intentando conectar a: {sepolia_node_url}")
web3 = Web3(Web3.HTTPProvider(sepolia_node_url))
print(f"¿Conectado a web3? {web3.is_connected()}")

contract_abi = None
try:
    abi_file_path = "./contracts/TournamentRegistry.json"
    print(f"Intentando abrir archivo ABI en: {abi_file_path}")
    with open(abi_file_path, 'r') as f:
        contract_abi = json.load(f)
    print("ABI cargada exitosamente.")
except FileNotFoundError:
    print("Error: El archivo TournamentRegistry.json no se encontró.")
    print("working directory:", os.getcwd())
    contract_abi = None
except json.JSONDecodeError:
    print("Error: El archivo TournamentRegistry.json contiene JSON inválido.")
    contract_abi = None

contract_address = os.getenv("CONTRACT_ADDRESS")
print(f"CONTRACT_ADDRESS (leído del entorno): {contract_address}")

private_key = os.getenv("SEPOLIA_PRIVATE_KEY")
if not private_key:
    print("Advertencia: La clave privada de Sepolia no se ha configurado como variable de entorno.")
else:
    print("Clave privada de Sepolia leída del entorno.")

contract = None
if contract_abi and web3.is_connected() and contract_address:
    try:
        print(f"Intentando inicializar contrato con dirección: {contract_address} y ABI...")
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        print("Contrato inicializado exitosamente.")
    except Exception as e:
        print(f"Error al inicializar el contrato: {e}")
else:
    print("No se pudo inicializar el contrato debido a problemas con web3:", web3.is_connected(), ", ABI:", contract_abi is not None, ", dirección:", contract_address is not None)

@csrf_exempt
def register_tournament_api(request):
    print("Función register_tournament_api llamada.")
    if request.method == 'POST':
        if not contract:
            print("Error: No se pudo inicializar el contrato dentro de la vista!!.")
            return JsonResponse({'error': 'No se pudo inicializar el contratowwe'}, status=500)
        if not web3.is_connected():
            print("Error: No se está conectado a la red Sepolia dentro de la vista!!.")
            return JsonResponse({'error': 'No se está conectado a la red Sepolia'}, status=500)
        if not private_key:
            print("Error: Clave privada no configurada dentro de la vista!!.")
            return JsonResponse({'error': 'Clave privada no configurada'}, status=500)

        try:
            data = json.loads(request.body)
            tournament_id = data.get('id')
            tournament_name = data.get('name')
            winner = data.get('winner')
            tree_hash = data.get('treeHash')

            # Validar que todos los campos necesarios estén presentes
            if not all([tournament_id, tournament_name, winner, tree_hash]):
                return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)

            # Obtener la cuenta desde la clave privada
            account = web3.eth.account.from_key(private_key)
            print(f"Cuenta obtenida: {account.address}")

            # Construir la transacción para llamar a la función registerTournament
            nonce = web3.eth.get_transaction_count(account.address)
            print(f"Nonce para la cuenta {account.address}: {nonce}")
            transaction = contract.functions.registerTournament(
                tournament_id,
                tournament_name,
                winner,
                tree_hash
            ).build_transaction({
                'gas': 600000,  # Estimar el gas necesario (puede necesitar ajuste)
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
            })
            print("Transacción construida.")

            # Firmar la transacción
            signed_transaction = account.sign_transaction(transaction)
            print("Transacción firmada.")

            # Enviar la transacción
            transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
            print(f"Transacción enviada. Hash: {transaction_hash.hex()}")

            return JsonResponse({'status': 'success', 'transaction_hash': transaction_hash.hex()})

        except json.JSONDecodeError:
            print("Error: Datos JSON inválidos en la solicitud.")
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            print(f"Error al registrar el torneo dentro de la vista: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print("Error: Método no permitido para /register.")
        return JsonResponse({'error': 'Método no permitido'}, status=405)