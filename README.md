# proyeccionweb
Procedimiento restarurar base de datos
pg_restore -U emelchor -d proyeccionesreal -1 backup_proyeccionesreal.dump

sudo -u postgres pg_dump -U postgres -d proyecciones -F c -f /var/lib/postgresql/backup_proyecciones.dump
