# Odoo14-PgAdmin

Este docker-compose es para la clase de DAM2, facilita el modo en el que podemos crear una base de datos de **Odoo con módulos personalizados** con **PgAdmin**.

## Modo de empleo
```Bash
cd Odoo14-PgAdmin/
```
```Bash
docker-compose up -d
```
### Odoo:
Después de ejecutar el comando anterior accederemos entrando al siguiente link (Puede tardar un poco): 
- http://localhost:8069

Una vez estamos dentro accemos al panel de control con estas credenciales: 
- *Usuario*: admin  
- *Contraseña*: admin

### PgAdmin:
Después de ejecutar el comando anterior accederemos entrando al siguiente link (Puede tardar un poco): 
- http://localhost:5050  

Una vez estamos dentro accemos al panel de control con estas credenciales:
- *Email*: admin@admin.com  
- *Contraseña*: admin 

Para configurar un nuevo servidor en PgAdmin necesitamos saber la ip del contenedor de la base de datos, para ello ejecutaremos el siguiente comando fuera del contenedor:
```Bash
docker inspect postgres | grep '"IPAddress"'
```
Seguido de eso solo tendríamos que insertar las credenciales de la base de datos:
- *Usuario*: odoo  
- *Contraseña*: odoo
