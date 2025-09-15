--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cuenta_contable; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.cuenta_contable (
    cuentaid integer NOT NULL,
    templateid integer NOT NULL,
    nivel integer,
    tipoid integer,
    codigo character varying(50) NOT NULL,
    nombre character varying(200) NOT NULL,
    proyeccion character(2),
    segmento character varying(150)
);


ALTER TABLE public.cuenta_contable OWNER TO emelchor;

--
-- Name: cuenta_contable_cuentaid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.cuenta_contable_cuentaid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cuenta_contable_cuentaid_seq OWNER TO emelchor;

--
-- Name: cuenta_contable_cuentaid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.cuenta_contable_cuentaid_seq OWNED BY public.cuenta_contable.cuentaid;


--
-- Name: grupo; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.grupo (
    grupoid integer NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.grupo OWNER TO emelchor;

--
-- Name: grupo_grupoid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.grupo_grupoid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grupo_grupoid_seq OWNER TO emelchor;

--
-- Name: grupo_grupoid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.grupo_grupoid_seq OWNED BY public.grupo.grupoid;


--
-- Name: indicador; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.indicador (
    indicadorid integer NOT NULL,
    grupoid integer,
    clavepais character(2),
    indicador character varying(150) NOT NULL,
    descripcion text,
    formula jsonb
);


ALTER TABLE public.indicador OWNER TO emelchor;

--
-- Name: indicador_indicadorid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.indicador_indicadorid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.indicador_indicadorid_seq OWNER TO emelchor;

--
-- Name: indicador_indicadorid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.indicador_indicadorid_seq OWNED BY public.indicador.indicadorid;


--
-- Name: institution; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.institution (
    institutionid integer NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    fecha_creacion timestamp without time zone DEFAULT now()
);


ALTER TABLE public.institution OWNER TO emelchor;

--
-- Name: institution_institutionid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.institution_institutionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institution_institutionid_seq OWNER TO emelchor;

--
-- Name: institution_institutionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.institution_institutionid_seq OWNED BY public.institution.institutionid;


--
-- Name: modelos; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.modelos (
    modeloid integer NOT NULL,
    cuentaid integer NOT NULL,
    modelo character varying(100),
    ubicacion character varying(250)
);


ALTER TABLE public.modelos OWNER TO emelchor;

--
-- Name: modelos_modeloid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.modelos_modeloid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.modelos_modeloid_seq OWNER TO emelchor;

--
-- Name: modelos_modeloid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.modelos_modeloid_seq OWNED BY public.modelos.modeloid;


--
-- Name: pais; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.pais (
    clavepais character(2) NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.pais OWNER TO emelchor;

--
-- Name: periodo; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.periodo (
    periodoid integer NOT NULL,
    anio integer NOT NULL,
    mes integer NOT NULL
);


ALTER TABLE public.periodo OWNER TO emelchor;

--
-- Name: periodo_periodoid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.periodo_periodoid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.periodo_periodoid_seq OWNER TO emelchor;

--
-- Name: periodo_periodoid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.periodo_periodoid_seq OWNED BY public.periodo.periodoid;


--
-- Name: predicciones; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.predicciones (
    prediccionid integer NOT NULL,
    modeloid integer NOT NULL,
    periodoid integer NOT NULL,
    prediccion numeric(18,2)
);


ALTER TABLE public.predicciones OWNER TO emelchor;

--
-- Name: predicciones_prediccionid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.predicciones_prediccionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.predicciones_prediccionid_seq OWNER TO emelchor;

--
-- Name: predicciones_prediccionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.predicciones_prediccionid_seq OWNED BY public.predicciones.prediccionid;


--
-- Name: saldo_mensual_cts; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.saldo_mensual_cts (
    saldoctsid integer NOT NULL,
    cuentaid integer NOT NULL,
    periodoid integer NOT NULL,
    saldo numeric(18,2)
);


ALTER TABLE public.saldo_mensual_cts OWNER TO emelchor;

--
-- Name: saldo_mensual_cts_saldoctsid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.saldo_mensual_cts_saldoctsid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saldo_mensual_cts_saldoctsid_seq OWNER TO emelchor;

--
-- Name: saldo_mensual_cts_saldoctsid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.saldo_mensual_cts_saldoctsid_seq OWNED BY public.saldo_mensual_cts.saldoctsid;


--
-- Name: sucursal; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.sucursal (
    sucursalid integer NOT NULL,
    institutionid integer NOT NULL,
    codigo character varying(50),
    nombre character varying(150)
);


ALTER TABLE public.sucursal OWNER TO emelchor;

--
-- Name: sucursal_sucursalid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.sucursal_sucursalid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sucursal_sucursalid_seq OWNER TO emelchor;

--
-- Name: sucursal_sucursalid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.sucursal_sucursalid_seq OWNED BY public.sucursal.sucursalid;


--
-- Name: sucursal_template; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.sucursal_template (
    suctempid integer NOT NULL,
    sucursalid integer NOT NULL,
    templateid integer NOT NULL,
    activo boolean DEFAULT false
);


ALTER TABLE public.sucursal_template OWNER TO emelchor;

--
-- Name: sucursal_template_suctempid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.sucursal_template_suctempid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sucursal_template_suctempid_seq OWNER TO emelchor;

--
-- Name: sucursal_template_suctempid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.sucursal_template_suctempid_seq OWNED BY public.sucursal_template.suctempid;


--
-- Name: tempind; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.tempind (
    indicadorid integer NOT NULL,
    templateid integer NOT NULL
);


ALTER TABLE public.tempind OWNER TO emelchor;

--
-- Name: template_balance; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.template_balance (
    templateid integer NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion character varying(250),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.template_balance OWNER TO emelchor;

--
-- Name: template_balance_templateid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.template_balance_templateid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.template_balance_templateid_seq OWNER TO emelchor;

--
-- Name: template_balance_templateid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.template_balance_templateid_seq OWNED BY public.template_balance.templateid;


--
-- Name: tempvar; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.tempvar (
    templateid integer NOT NULL,
    variableid integer NOT NULL
);


ALTER TABLE public.tempvar OWNER TO emelchor;

--
-- Name: tipocuenta; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.tipocuenta (
    tipocuentaid integer NOT NULL,
    clavetipo character varying(2),
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.tipocuenta OWNER TO emelchor;

--
-- Name: tipocuenta_tipocuentaid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.tipocuenta_tipocuentaid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipocuenta_tipocuentaid_seq OWNER TO emelchor;

--
-- Name: tipocuenta_tipocuentaid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.tipocuenta_tipocuentaid_seq OWNED BY public.tipocuenta.tipocuentaid;


--
-- Name: valor_variable; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.valor_variable (
    valorvariableid integer NOT NULL,
    variableid integer NOT NULL,
    periodoid integer NOT NULL,
    valor numeric(10,2)
);


ALTER TABLE public.valor_variable OWNER TO emelchor;

--
-- Name: valor_variable_valorvariableid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.valor_variable_valorvariableid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.valor_variable_valorvariableid_seq OWNER TO emelchor;

--
-- Name: valor_variable_valorvariableid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.valor_variable_valorvariableid_seq OWNED BY public.valor_variable.valorvariableid;


--
-- Name: valorindicador; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.valorindicador (
    valorindid integer NOT NULL,
    indicadorid integer NOT NULL,
    periodoid integer NOT NULL,
    valor numeric(18,2)
);


ALTER TABLE public.valorindicador OWNER TO emelchor;

--
-- Name: valorindicador_valorindid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.valorindicador_valorindid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.valorindicador_valorindid_seq OWNER TO emelchor;

--
-- Name: valorindicador_valorindid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.valorindicador_valorindid_seq OWNED BY public.valorindicador.valorindid;


--
-- Name: variables; Type: TABLE; Schema: public; Owner: emelchor
--

CREATE TABLE public.variables (
    variableid integer NOT NULL,
    nombrevariable character varying(100) NOT NULL,
    descripcionvariable text,
    clavepais character(2)
);


ALTER TABLE public.variables OWNER TO emelchor;

--
-- Name: variables_variableid_seq; Type: SEQUENCE; Schema: public; Owner: emelchor
--

CREATE SEQUENCE public.variables_variableid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.variables_variableid_seq OWNER TO emelchor;

--
-- Name: variables_variableid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emelchor
--

ALTER SEQUENCE public.variables_variableid_seq OWNED BY public.variables.variableid;


--
-- Name: cuenta_contable cuentaid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.cuenta_contable ALTER COLUMN cuentaid SET DEFAULT nextval('public.cuenta_contable_cuentaid_seq'::regclass);


--
-- Name: grupo grupoid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.grupo ALTER COLUMN grupoid SET DEFAULT nextval('public.grupo_grupoid_seq'::regclass);


--
-- Name: indicador indicadorid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.indicador ALTER COLUMN indicadorid SET DEFAULT nextval('public.indicador_indicadorid_seq'::regclass);


--
-- Name: institution institutionid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.institution ALTER COLUMN institutionid SET DEFAULT nextval('public.institution_institutionid_seq'::regclass);


--
-- Name: modelos modeloid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.modelos ALTER COLUMN modeloid SET DEFAULT nextval('public.modelos_modeloid_seq'::regclass);


--
-- Name: periodo periodoid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.periodo ALTER COLUMN periodoid SET DEFAULT nextval('public.periodo_periodoid_seq'::regclass);


--
-- Name: predicciones prediccionid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.predicciones ALTER COLUMN prediccionid SET DEFAULT nextval('public.predicciones_prediccionid_seq'::regclass);


--
-- Name: saldo_mensual_cts saldoctsid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.saldo_mensual_cts ALTER COLUMN saldoctsid SET DEFAULT nextval('public.saldo_mensual_cts_saldoctsid_seq'::regclass);


--
-- Name: sucursal sucursalid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal ALTER COLUMN sucursalid SET DEFAULT nextval('public.sucursal_sucursalid_seq'::regclass);


--
-- Name: sucursal_template suctempid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal_template ALTER COLUMN suctempid SET DEFAULT nextval('public.sucursal_template_suctempid_seq'::regclass);


--
-- Name: template_balance templateid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.template_balance ALTER COLUMN templateid SET DEFAULT nextval('public.template_balance_templateid_seq'::regclass);


--
-- Name: tipocuenta tipocuentaid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tipocuenta ALTER COLUMN tipocuentaid SET DEFAULT nextval('public.tipocuenta_tipocuentaid_seq'::regclass);


--
-- Name: valor_variable valorvariableid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valor_variable ALTER COLUMN valorvariableid SET DEFAULT nextval('public.valor_variable_valorvariableid_seq'::regclass);


--
-- Name: valorindicador valorindid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valorindicador ALTER COLUMN valorindid SET DEFAULT nextval('public.valorindicador_valorindid_seq'::regclass);


--
-- Name: variables variableid; Type: DEFAULT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.variables ALTER COLUMN variableid SET DEFAULT nextval('public.variables_variableid_seq'::regclass);


--
-- Data for Name: cuenta_contable; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.cuenta_contable (cuentaid, templateid, nivel, tipoid, codigo, nombre, proyeccion, segmento) FROM stdin;
1	1	1	1	1	Activo	NO	
2	1	2	1	101	Disponibilidades	SI	
3	1	2	1	102	Inversiones en valores	SI	
4	2	1	1	1	Activo	NO	
5	2	2	1	101	Disponibilidades	SI	
6	2	2	1	102	Inversiones en valores	SI	
\.


--
-- Data for Name: grupo; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.grupo (grupoid, nombre) FROM stdin;
1	Capitalización
\.


--
-- Data for Name: indicador; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.indicador (indicadorid, grupoid, clavepais, indicador, descripcion, formula) FROM stdin;
1	1	MX	Rentabilidad	Indicador de rentabilidad anual	{"numerador": "utilidad_neta", "denominador": "activos_totales"}
2	1	MX	Rentabilidad	Indicador de rentabilidad anual	{"numerador": "utilidad_neta", "denominador": "activos_totales"}
\.


--
-- Data for Name: institution; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.institution (institutionid, nombre, descripcion, fecha_creacion) FROM stdin;
1	Instituto ABC	Descripción del instituto	2025-09-14 07:22:39.421416
\.


--
-- Data for Name: modelos; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.modelos (modeloid, cuentaid, modelo, ubicacion) FROM stdin;
1	1	Modelo de Proyección ABC	/archivos/modelo_abc.xlsx
2	2	Modelo de Proyección ABC	/archivos/modelo_abc.xlsx
3	6	Modelo de Proyección ABC	/archivos/modelo_abc.xlsx
\.


--
-- Data for Name: pais; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.pais (clavepais, nombre) FROM stdin;
AF	Afghanistan
AL	Albania
DZ	Algeria
AS	American Samoa
AD	Andorra
AO	Angola
AI	Anguilla
AQ	Antarctica
AG	Antigua and Barbuda
AR	Argentina
AM	Armenia
AW	Aruba
AU	Australia
AT	Austria
AZ	Azerbaijan
BS	Bahamas
BH	Bahrain
BD	Bangladesh
BB	Barbados
BY	Belarus
BE	Belgium
BZ	Belize
BJ	Benin
BM	Bermuda
BT	Bhutan
BO	Bolivia
BA	Bosnia and Herzegovina
BW	Botswana
BR	Brazil
BN	Brunei Darussalam
BG	Bulgaria
BF	Burkina Faso
BI	Burundi
CV	Cabo Verde
KH	Cambodia
CM	Cameroon
CA	Canada
KY	Cayman Islands
CF	Central African Republic
TD	Chad
CL	Chile
CN	China
CO	Colombia
KM	Comoros
CG	Congo
CD	Congo, Democratic Republic of the
CR	Costa Rica
HR	Croatia
CU	Cuba
CY	Cyprus
CZ	Czechia
DK	Denmark
DJ	Djibouti
DM	Dominica
DO	Dominican Republic
EC	Ecuador
EG	Egypt
SV	El Salvador
GQ	Equatorial Guinea
ER	Eritrea
EE	Estonia
SZ	Eswatini
ET	Ethiopia
FJ	Fiji
FI	Finland
FR	France
GA	Gabon
GM	Gambia
GE	Georgia
DE	Germany
GH	Ghana
GR	Greece
GD	Grenada
GT	Guatemala
GN	Guinea
GW	Guinea-Bissau
GY	Guyana
HT	Haiti
VA	Holy See
HN	Honduras
HU	Hungary
IS	Iceland
IN	India
ID	Indonesia
IR	Iran
IQ	Iraq
IE	Ireland
IL	Israel
IT	Italy
JM	Jamaica
JP	Japan
JO	Jordan
KZ	Kazakhstan
KE	Kenya
KI	Kiribati
KP	Korea, Democratic People's Republic of
KR	Korea, Republic of
KW	Kuwait
KG	Kyrgyzstan
LA	Lao People's Democratic Republic
LV	Latvia
LB	Lebanon
LS	Lesotho
LR	Liberia
LY	Libya
LI	Liechtenstein
LT	Lithuania
LU	Luxembourg
MG	Madagascar
MW	Malawi
MY	Malaysia
MV	Maldives
ML	Mali
MT	Malta
MH	Marshall Islands
MR	Mauritania
MU	Mauritius
MX	Mexico
FM	Micronesia
MD	Moldova
MC	Monaco
MN	Mongolia
ME	Montenegro
MA	Morocco
MZ	Mozambique
MM	Myanmar
NA	Namibia
NR	Nauru
NP	Nepal
NL	Netherlands
NZ	New Zealand
NI	Nicaragua
NE	Niger
NG	Nigeria
MK	North Macedonia
NO	Norway
OM	Oman
PK	Pakistan
PW	Palau
PS	Palestine, State of
PA	Panama
PG	Papua New Guinea
PY	Paraguay
PE	Peru
PH	Philippines
PL	Poland
PT	Portugal
QA	Qatar
RO	Romania
RU	Russian Federation
RW	Rwanda
KN	Saint Kitts and Nevis
LC	Saint Lucia
VC	Saint Vincent and the Grenadines
WS	Samoa
SM	San Marino
ST	Sao Tome and Principe
SA	Saudi Arabia
SN	Senegal
RS	Serbia
SC	Seychelles
SL	Sierra Leone
SG	Singapore
SK	Slovakia
SI	Slovenia
SB	Solomon Islands
SO	Somalia
ZA	South Africa
SS	South Sudan
ES	Spain
LK	Sri Lanka
SD	Sudan
SR	Suriname
SE	Sweden
CH	Switzerland
SY	Syrian Arab Republic
TW	Taiwan, Province of China
TJ	Tajikistan
TZ	Tanzania
TH	Thailand
TL	Timor-Leste
TG	Togo
TO	Tonga
TT	Trinidad and Tobago
TN	Tunisia
TR	Türkiye
TM	Turkmenistan
TV	Tuvalu
UG	Uganda
UA	Ukraine
AE	United Arab Emirates
GB	United Kingdom
US	United States
UY	Uruguay
UZ	Uzbekistan
VU	Vanuatu
VE	Venezuela
VN	Viet Nam
YE	Yemen
ZM	Zambia
ZW	Zimbabwe
\.


--
-- Data for Name: periodo; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.periodo (periodoid, anio, mes) FROM stdin;
1	2025	1
2	2025	2
3	2025	3
4	2025	4
5	2025	5
6	2025	6
7	2025	7
8	2025	8
9	2025	9
10	2025	10
11	2025	11
12	2025	12
13	2026	1
\.


--
-- Data for Name: predicciones; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.predicciones (prediccionid, modeloid, periodoid, prediccion) FROM stdin;
1	1	5	125000.50
2	3	5	125000.50
\.


--
-- Data for Name: saldo_mensual_cts; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.saldo_mensual_cts (saldoctsid, cuentaid, periodoid, saldo) FROM stdin;
\.


--
-- Data for Name: sucursal; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.sucursal (sucursalid, institutionid, codigo, nombre) FROM stdin;
1	1	01	Matriz
\.


--
-- Data for Name: sucursal_template; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.sucursal_template (suctempid, sucursalid, templateid, activo) FROM stdin;
1	1	1	f
2	1	2	t
\.


--
-- Data for Name: tempind; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.tempind (indicadorid, templateid) FROM stdin;
1	1
\.


--
-- Data for Name: template_balance; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.template_balance (templateid, nombre, descripcion, created_at) FROM stdin;
1	NombreActualizado	Descripción actualizada	2025-09-14 07:52:05.42612
2	Template Segundo	Template Para las SOCAPs	2025-09-14 10:11:52.07599
\.


--
-- Data for Name: tempvar; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.tempvar (templateid, variableid) FROM stdin;
1	4
\.


--
-- Data for Name: tipocuenta; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.tipocuenta (tipocuentaid, clavetipo, nombre) FROM stdin;
1	A	Activo
2	P	Pasivo
\.


--
-- Data for Name: valor_variable; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.valor_variable (valorvariableid, variableid, periodoid, valor) FROM stdin;
1	4	3	15.20
2	6	4	19.99
\.


--
-- Data for Name: valorindicador; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.valorindicador (valorindid, indicadorid, periodoid, valor) FROM stdin;
1	1	5	123.45
\.


--
-- Data for Name: variables; Type: TABLE DATA; Schema: public; Owner: emelchor
--

COPY public.variables (variableid, nombrevariable, descripcionvariable, clavepais) FROM stdin;
4	Inflación	Tasa de inflación anual	MX
5	PIB	Producto Interno Bruto trimestral	US
6	Desempleo	Tasa de desempleo mensual	MX
\.


--
-- Name: cuenta_contable_cuentaid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.cuenta_contable_cuentaid_seq', 6, true);


--
-- Name: grupo_grupoid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.grupo_grupoid_seq', 1, true);


--
-- Name: indicador_indicadorid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.indicador_indicadorid_seq', 2, true);


--
-- Name: institution_institutionid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.institution_institutionid_seq', 1, true);


--
-- Name: modelos_modeloid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.modelos_modeloid_seq', 3, true);


--
-- Name: periodo_periodoid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.periodo_periodoid_seq', 13, true);


--
-- Name: predicciones_prediccionid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.predicciones_prediccionid_seq', 2, true);


--
-- Name: saldo_mensual_cts_saldoctsid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.saldo_mensual_cts_saldoctsid_seq', 1, false);


--
-- Name: sucursal_sucursalid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.sucursal_sucursalid_seq', 1, true);


--
-- Name: sucursal_template_suctempid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.sucursal_template_suctempid_seq', 2, true);


--
-- Name: template_balance_templateid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.template_balance_templateid_seq', 2, true);


--
-- Name: tipocuenta_tipocuentaid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.tipocuenta_tipocuentaid_seq', 2, true);


--
-- Name: valor_variable_valorvariableid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.valor_variable_valorvariableid_seq', 2, true);


--
-- Name: valorindicador_valorindid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.valorindicador_valorindid_seq', 1, true);


--
-- Name: variables_variableid_seq; Type: SEQUENCE SET; Schema: public; Owner: emelchor
--

SELECT pg_catalog.setval('public.variables_variableid_seq', 6, true);


--
-- Name: cuenta_contable cuenta_contable_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.cuenta_contable
    ADD CONSTRAINT cuenta_contable_pkey PRIMARY KEY (cuentaid);


--
-- Name: grupo grupo_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.grupo
    ADD CONSTRAINT grupo_pkey PRIMARY KEY (grupoid);


--
-- Name: indicador indicador_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.indicador
    ADD CONSTRAINT indicador_pkey PRIMARY KEY (indicadorid);


--
-- Name: institution institution_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.institution
    ADD CONSTRAINT institution_pkey PRIMARY KEY (institutionid);


--
-- Name: modelos modelos_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.modelos
    ADD CONSTRAINT modelos_pkey PRIMARY KEY (modeloid);


--
-- Name: pais pais_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.pais
    ADD CONSTRAINT pais_pkey PRIMARY KEY (clavepais);


--
-- Name: periodo periodo_anio_mes_key; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.periodo
    ADD CONSTRAINT periodo_anio_mes_key UNIQUE (anio, mes);


--
-- Name: periodo periodo_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.periodo
    ADD CONSTRAINT periodo_pkey PRIMARY KEY (periodoid);


--
-- Name: predicciones predicciones_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT predicciones_pkey PRIMARY KEY (prediccionid);


--
-- Name: saldo_mensual_cts saldo_mensual_cts_cuentaid_periodoid_key; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.saldo_mensual_cts
    ADD CONSTRAINT saldo_mensual_cts_cuentaid_periodoid_key UNIQUE (cuentaid, periodoid);


--
-- Name: saldo_mensual_cts saldo_mensual_cts_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.saldo_mensual_cts
    ADD CONSTRAINT saldo_mensual_cts_pkey PRIMARY KEY (saldoctsid);


--
-- Name: sucursal sucursal_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_pkey PRIMARY KEY (sucursalid);


--
-- Name: sucursal_template sucursal_template_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal_template
    ADD CONSTRAINT sucursal_template_pkey PRIMARY KEY (suctempid);


--
-- Name: sucursal_template sucursal_template_sucursalid_templateid_key; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal_template
    ADD CONSTRAINT sucursal_template_sucursalid_templateid_key UNIQUE (sucursalid, templateid);


--
-- Name: tempind tempind_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempind
    ADD CONSTRAINT tempind_pkey PRIMARY KEY (indicadorid, templateid);


--
-- Name: template_balance template_balance_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.template_balance
    ADD CONSTRAINT template_balance_pkey PRIMARY KEY (templateid);


--
-- Name: tempvar tempvar_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempvar
    ADD CONSTRAINT tempvar_pkey PRIMARY KEY (templateid, variableid);


--
-- Name: tipocuenta tipocuenta_nombre_key; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tipocuenta
    ADD CONSTRAINT tipocuenta_nombre_key UNIQUE (nombre);


--
-- Name: tipocuenta tipocuenta_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tipocuenta
    ADD CONSTRAINT tipocuenta_pkey PRIMARY KEY (tipocuentaid);


--
-- Name: valor_variable valor_variable_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valor_variable
    ADD CONSTRAINT valor_variable_pkey PRIMARY KEY (valorvariableid);


--
-- Name: valorindicador valorindicador_indicadorid_periodoid_key; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valorindicador
    ADD CONSTRAINT valorindicador_indicadorid_periodoid_key UNIQUE (indicadorid, periodoid);


--
-- Name: valorindicador valorindicador_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valorindicador
    ADD CONSTRAINT valorindicador_pkey PRIMARY KEY (valorindid);


--
-- Name: variables variables_pkey; Type: CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.variables
    ADD CONSTRAINT variables_pkey PRIMARY KEY (variableid);


--
-- Name: unico_template_activo; Type: INDEX; Schema: public; Owner: emelchor
--

CREATE UNIQUE INDEX unico_template_activo ON public.sucursal_template USING btree (sucursalid) WHERE (activo = true);


--
-- Name: cuenta_contable cuenta_contable_templateid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.cuenta_contable
    ADD CONSTRAINT cuenta_contable_templateid_fkey FOREIGN KEY (templateid) REFERENCES public.template_balance(templateid) ON DELETE CASCADE;


--
-- Name: cuenta_contable cuenta_contable_tipoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.cuenta_contable
    ADD CONSTRAINT cuenta_contable_tipoid_fkey FOREIGN KEY (tipoid) REFERENCES public.tipocuenta(tipocuentaid);


--
-- Name: indicador indicador_clavepais_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.indicador
    ADD CONSTRAINT indicador_clavepais_fkey FOREIGN KEY (clavepais) REFERENCES public.pais(clavepais);


--
-- Name: indicador indicador_grupoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.indicador
    ADD CONSTRAINT indicador_grupoid_fkey FOREIGN KEY (grupoid) REFERENCES public.grupo(grupoid) ON DELETE CASCADE;


--
-- Name: modelos modelos_cuentaid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.modelos
    ADD CONSTRAINT modelos_cuentaid_fkey FOREIGN KEY (cuentaid) REFERENCES public.cuenta_contable(cuentaid) ON DELETE CASCADE;


--
-- Name: predicciones predicciones_modeloid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT predicciones_modeloid_fkey FOREIGN KEY (modeloid) REFERENCES public.modelos(modeloid) ON DELETE CASCADE;


--
-- Name: predicciones predicciones_periodoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT predicciones_periodoid_fkey FOREIGN KEY (periodoid) REFERENCES public.periodo(periodoid);


--
-- Name: saldo_mensual_cts saldo_mensual_cts_cuentaid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.saldo_mensual_cts
    ADD CONSTRAINT saldo_mensual_cts_cuentaid_fkey FOREIGN KEY (cuentaid) REFERENCES public.cuenta_contable(cuentaid) ON DELETE CASCADE;


--
-- Name: saldo_mensual_cts saldo_mensual_cts_periodoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.saldo_mensual_cts
    ADD CONSTRAINT saldo_mensual_cts_periodoid_fkey FOREIGN KEY (periodoid) REFERENCES public.periodo(periodoid);


--
-- Name: sucursal sucursal_institutionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_institutionid_fkey FOREIGN KEY (institutionid) REFERENCES public.institution(institutionid) ON DELETE CASCADE;


--
-- Name: sucursal_template sucursal_template_sucursalid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal_template
    ADD CONSTRAINT sucursal_template_sucursalid_fkey FOREIGN KEY (sucursalid) REFERENCES public.sucursal(sucursalid) ON DELETE CASCADE;


--
-- Name: sucursal_template sucursal_template_templateid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.sucursal_template
    ADD CONSTRAINT sucursal_template_templateid_fkey FOREIGN KEY (templateid) REFERENCES public.template_balance(templateid) ON DELETE CASCADE;


--
-- Name: tempind tempind_indicadorid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempind
    ADD CONSTRAINT tempind_indicadorid_fkey FOREIGN KEY (indicadorid) REFERENCES public.indicador(indicadorid) ON DELETE CASCADE;


--
-- Name: tempind tempind_templateid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempind
    ADD CONSTRAINT tempind_templateid_fkey FOREIGN KEY (templateid) REFERENCES public.template_balance(templateid) ON DELETE CASCADE;


--
-- Name: tempvar tempvar_templateid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempvar
    ADD CONSTRAINT tempvar_templateid_fkey FOREIGN KEY (templateid) REFERENCES public.template_balance(templateid) ON DELETE CASCADE;


--
-- Name: tempvar tempvar_variableid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.tempvar
    ADD CONSTRAINT tempvar_variableid_fkey FOREIGN KEY (variableid) REFERENCES public.variables(variableid) ON DELETE CASCADE;


--
-- Name: valor_variable valor_variable_periodoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valor_variable
    ADD CONSTRAINT valor_variable_periodoid_fkey FOREIGN KEY (periodoid) REFERENCES public.periodo(periodoid);


--
-- Name: valor_variable valor_variable_variableid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valor_variable
    ADD CONSTRAINT valor_variable_variableid_fkey FOREIGN KEY (variableid) REFERENCES public.variables(variableid) ON DELETE CASCADE;


--
-- Name: valorindicador valorindicador_indicadorid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valorindicador
    ADD CONSTRAINT valorindicador_indicadorid_fkey FOREIGN KEY (indicadorid) REFERENCES public.indicador(indicadorid) ON DELETE CASCADE;


--
-- Name: valorindicador valorindicador_periodoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.valorindicador
    ADD CONSTRAINT valorindicador_periodoid_fkey FOREIGN KEY (periodoid) REFERENCES public.periodo(periodoid);


--
-- Name: variables variables_clavepais_fkey; Type: FK CONSTRAINT; Schema: public; Owner: emelchor
--

ALTER TABLE ONLY public.variables
    ADD CONSTRAINT variables_clavepais_fkey FOREIGN KEY (clavepais) REFERENCES public.pais(clavepais);


--
-- PostgreSQL database dump complete
--

