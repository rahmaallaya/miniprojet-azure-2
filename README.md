# Mini projet : site web dynamique sur Azure (3 VM, 3 VNets)

Application CRUD « Gestion d'Instruments » déployée en 3 tiers sur Azure.
Groupe de ressources : `rg-miniprojet-rahma` (région Spain Central).

## Architecture

| Tier | VM | VNet | Sous-réseau | IP privée | IP publique | Service |
|---|---|---|---|---|---|---|
| Présentation | vm-web | vnet-web 10.1.0.0/16 | 10.1.1.0/24 | 10.1.1.4 | oui | Nginx (reverse proxy + frontend) |
| Logique métier | vm-app | vnet-app 10.2.0.0/16 | 10.2.1.0/24 | 10.2.1.4 | aucune | API Flask (port 5000) |
| Données | vm-db | vnet-db 10.3.0.0/16 | 10.3.1.0/24 | 10.3.1.4 | aucune | MySQL 8 (port 3306) |

Peering : vnet-web <-> vnet-app et vnet-app <-> vnet-db.
Le peering n'est pas transitif : vm-web ne peut pas joindre vm-db directement.

## Contenu du dépôt

- `backend/app.py` : API REST Flask (CRUD sur `/api/instruments`)
- `frontend/index.html`, `frontend/app.js` : interface (Bootstrap + fetch)
- `config/nginx-default.conf` : reverse proxy vers vm-app
- `config/api.service` : service systemd de l'API
- `schema.sql` : base, utilisateur dédié, table et données de test

Le mot de passe MySQL est remplacé par `CHANGE_ME` dans le code publié.

## Règles NSG (principe du moindre privilège)

| NSG | Règle | Source | Port |
|---|---|---|---|
| nsg-web | Allow-HTTP-HTTPS | Internet | 80, 443 |
| nsg-web | Allow-SSH-Admin | IP de l'administrateur /32 | 22 |
| nsg-app | Allow-API | 10.1.1.0/24 | 5000 |
| nsg-app | Allow-SSH-Web | 10.1.1.0/24 | 22 |
| nsg-db | Allow-DB | 10.2.1.0/24 | 3306 |
| nsg-db | Allow-SSH-App | 10.2.1.0/24 | 22 |
| tous | Deny-All | * | * |

## Accès SSH (fichier ~/.ssh/config)

```
Host vm-web
  HostName <IP_PUBLIQUE_VM_WEB>
  User azureuser
  IdentityFile ~/.ssh/miniprojet_key

Host vm-app
  HostName 10.2.1.4
  User azureuser
  IdentityFile ~/.ssh/miniprojet_key
  ProxyJump vm-web

Host vm-db
  HostName 10.3.1.4
  User azureuser
  IdentityFile ~/.ssh/miniprojet_key
  ProxyJump vm-app
```

## Commandes principales

NAT Gateway (nécessaire pour que vm-app et vm-db téléchargent leurs paquets sans IP publique) :

```bash
az network public-ip create -g $RG -l $LOC -n pip-nat --sku Standard
az network nat gateway create -g $RG -l $LOC -n nat-gw --public-ip-addresses pip-nat --idle-timeout 10
az network vnet subnet update -g $RG --vnet-name vnet-app -n subnet-app --nat-gateway nat-gw

az network public-ip create -g $RG -l $LOC -n pip-nat-db --sku Standard
az network nat gateway create -g $RG -l $LOC -n nat-gw-db --public-ip-addresses pip-nat-db --idle-timeout 10
az network vnet subnet update -g $RG --vnet-name vnet-db -n subnet-db --nat-gateway nat-gw-db
```

Restriction du SSH à l'IP de l'administrateur :

```bash
az network nsg rule update -g $RG --nsg-name nsg-web -n Allow-SSH-Admin --source-address-prefixes <IP>/32
```

vm-db :

```bash
sudo apt update && sudo apt install -y mysql-server
sudo sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql
sudo mysql < schema.sql
```

vm-app :

```bash
sudo apt update && sudo apt install -y python3-flask python3-pymysql
# copier backend/app.py dans ~/api/ et config/api.service dans /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now api
```

vm-web :

```bash
sudo apt update && sudo apt install -y nginx
# copier config/nginx-default.conf vers /etc/nginx/sites-available/default
# copier frontend/* dans /var/www/html/
sudo nginx -t && sudo systemctl reload nginx
```

Preuve de non-transitivité du peering (depuis vm-web) :

```bash
nc -zv -w 5 10.2.1.4 5000   # réussit
nc -zv -w 5 10.3.1.4 3306   # échoue (timeout)
```

## Nettoyage

```bash
az group delete -n rg-miniprojet-rahma --yes --no-wait
```
[Uploading schema.sql…]()
