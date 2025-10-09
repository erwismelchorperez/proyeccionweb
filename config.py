class Config:
    SECRET_KEY = 'clave_secreta_segura'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://proyeccion:proyecc10n35@localhost:5432/proyecciones'
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://emelchor:Emelch0r1*@localhost:5432/proyeccionesreal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
