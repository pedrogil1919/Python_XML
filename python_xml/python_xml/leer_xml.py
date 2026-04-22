"""
Created on 9 may 2024

Funciones para leer y guardar datos del archivo xml de configuración.

@author: pedrogil

"""
from tkinter import messagebox
from xml.etree import ElementTree


# Nombre del archivo xml, por si queremos modificar su contenido
nombre_xml = None
# Raíz del contenido del archivo xml
archivo_xml = None


###############################################################################
# FUNCIONES GENERALES
###############################################################################

# Definición de una función que emplearemos como decorator, para seguir la
# misma estrategia en todas las funciones de lectura del archivo xml en caso de
# error en el propio archivo xml.


def captura_error(funcion_leer_xml):
    """
    Función decorator

    Esta función realiza la llamada a la función de lectura de algún campo xml,
    capturando el error que genera el propio archivo, y sacando un mensaje por
    pantalla en caso de error en el archivo.

    """
    def control(*argumentos):
        try:
            # # Llamamos a la función de lectura del xml.
            # if len(argumentos) == 0:
            #     # NOTA: Si el argumento es None, se supone que estamos
            #     # realizando la llamada a una función que no acepta argumentos.
            #     res = funcion_leer_xml()
            # else:
            #     # Sin embargo, si no es None, es una función que acepta un
            #     # argumento.
            #     res = funcion_leer_xml(*argumentos)
            res = funcion_leer_xml(*argumentos)
            # Y devolvemos los datos leidos.
            return res
        except (AttributeError, KeyError):
            # Si hay algún error en el archivo xml, como que falta la clave o
            # el parámetro, mostramos un mensaje de error.
            messagebox.showerror(
                "Error configuración",
                "Error en el archivo de configuración %s. "
                "Revisar parámetros del elemento '%s'" %
                (nombre_xml, argumentos[0]))
            exit(1)
        except ValueError:
            # Si hay algún error en el archivo xml, como que falta la clave o
            # el parámetro, mostramos un mensaje de error.
            messagebox.showerror(
                "Error configuración",
                "Error en el archivo de configuración %s. "
                "Revisar parámetros del elemento '%s' / '%s'" %
                (nombre_xml, argumentos[0], argumentos[1]))
            exit(1)
    return control


def abrir_archivo_xml(archivo, guardar=True):
    """
    Abrir y guardar en el módulo el archivo xml de configuración.

    Si guardar es igual a True, el archivo y su nombre se guardan en el módulo
    para futuras lecturas / escrituras del archivo xml.

    En cualquier caso, se devuelve una referencia al archivo abierto.

    """
    global archivo_xml
    global nombre_xml
    try:
        xml_aux = ElementTree.parse(archivo)
    except ElementTree.ParseError as error:
        raise RuntimeError("Error archivo XML %s: %s." % (archivo, error))
    if guardar:
        # Nos solicitan guardar una referencia del archivo.
        archivo_xml = xml_aux
        nombre_xml = archivo
    return xml_aux


def txt2bool(valor):
    """
    Función para convertir el valor del xml a booleano

    """
    c = {
        "TRUE": True,
        "FALSE": False,
        "T": True,
        "F": False,
        "1": True,
        "0": False}
    valor = valor.upper()
    return c[valor]


def bool2txt(valor):
    """
    Función para convertir un bool en un texto para archivos xml

    """
    return "TRUE" if valor else "FALSE"


conversion_tipo = {
    's': lambda: None,
    'i': int,
    'f': float,
    'b': txt2bool}


def convertir_tipo(valor, formato):
    try:
        return conversion_tipo[formato](valor)
    except Exception:
        return valor


def convertir_tipo_inv(valor, formato):
    if formato == 'b':
        return bool2txt(valor)
    elif formato == 's':
        return valor
    return str(valor)


def aux_atributos_xml(elemento, atributos, formatos=None, valores=None):
    """
    Devuelve o actualiza los atributos solicitados de un elemento.

    Argumentos:
    - elemento: ElementTree del elemento sobre el cual queremos obtener o
      actualizar sus atributos.
    - atributos, formatos: ver función leer_atributos_xml
    - valores: si es None, la función devuelve los atributos solicitados.
      Si es una lista de la misma longitud que atributos, actualiza los
      atributos con la lista indicada. Si la longitud de valores no es la misma
      que la de atributos, lanza una excepción de tipo ValueError.

    """
    # Comprobamos si nos están pidiendo más de un atributo.
    if isinstance(atributos, (list, tuple)):
        N = len(atributos)
    else:
        N = 1

    # Comprobamos el valor de la variable formato.
    if formatos is None:
        # Si no nos pasan ningún formato, se entiende que todas son string y
        # no hay que hacer ninguna conversión.
        formatos = "s" * N
    elif not isinstance(formatos, str):
        raise ValueError("Formato de atributos xml incorrecto.")
    elif len(formatos) == 1:
        # Sí solo nos pasan un dato, se entiende que todos los atributos
        # tienen el mismo formato.
        formatos = formatos * N
    elif len(formatos) < N:
        # Si la longitud de formatos es menor que la de atributos, los que
        # faltan se supone que son string.
        formatos = formatos + "s" * (N - len(formatos))

    # Comprobamos si debemos devolver los atributos, o actualizarlos.
    if valores is None:
        # En este caso, nos están solicitando los valores actuales de los
        # atributos.
        if not isinstance(atributos, (list, tuple)):
            # Sí solo nos piden uno y no es una lista, lo devolvemos como una
            # única variable.
            valor = elemento.attrib[atributos]
            lista = convertir_tipo(valor, formatos[0])
        else:
            # Si nos mandan una lista, aunque sea de un sólo elemento, lo
            # devolvemos como un diccionario.
            lista = {}
            for atributo, formato in zip(atributos, formatos):
                valor = elemento.attrib[atributo]
                valor = convertir_tipo(valor, formato)
                lista[atributo] = valor
        return lista
    # En caso contario, nos solicitan actualizar los valores y guardarlos en el
    # archivo xml.
    # Comprobamos si nos han pasado una lista, o solo un valor.
    if not isinstance(valores, (list, tuple)):
        valores = (valores,)
    M = len(valores)
    # Comprobamos que las longitudes coincidan.
    if M != N:
        raise ValueError(
            "Lista de valores no coincide con lista de atributos xml.")
    if not isinstance(atributos, (list, tuple)):
        atributos = (atributos,)
    for atributo, formato, valor in zip(atributos, formatos, valores):
        # Convertimos el formato del archivo.
        valor = convertir_tipo_inv(valor, formato)
        # Y lo guardamos en la lista de el elemento.
        elemento.attrib[atributo] = valor

###############################################################################
# FUNCIONES DE LECTURA DE ARCHIVOS XML GENERALES
###############################################################################


@captura_error
def leer_atributos_xml(elementos, atributos, formatos=None, archivo=None):
    """
    Obtiene los atributos de un elemento, 

    Argumentos:
    - elementos: nombre del elemento del cual queremos obtener sus atributos.
      Si se trata de un elemento anidado, elementos debe ser una lista con
      todos los elementos que hay que atravesar, empezando por el de mayor
      nivel.
    - atributos: lista de atributos. Si esta variable sólo tiene un elemento,
      se devuelve su valor como una variable. Si tiene más elementos, se
      devuelve como un diccionario.
    - formatos: formatea el tipo de datos. Se trata de una cadena de caracteres, 
      cuyos valores pueden ser:
      - s: cadena de caracteres (no hacer conversión).
      - i: entero.
      - f: decimal.
      Si está vacio, no existe o es erréneo, no se hace ningún tipo de
      conversión.
      Si la cadena sólo tiene un carácter, se aplica el mismo formato a todos
      los elementos. Si tiene más caracteres, su longitud debe ser igual a la
      de la variable atributos.
    - archivo: archivo xml de donde obtener la información. Si es None, se
      obtiene del archivo previamente abierto con abrir_archivo_xml

###########################################################################
# Archivo prueba.xml
###########################################################################
<?xml version='1.0' encoding='utf-8'?>
<prueba>
    <elemento1 TAG1="24" TAG2="hola">
        <elemento2 TAG3="otro" TAG7="más">
            <elemento3>
                <elemento4 TAG4="prueba" TAG5="14.2" TAG6="otra">
                </elemento4>
            </elemento3>
        </elemento2>
    </elemento1>
</prueba>
###########################################################################

###########################################################################
# Archivo prueba.py
###########################################################################
from python_comun import abrir_archivo_xml
from python_comun import leer_atributos_xml

abrir_archivo_xml("prueba.xml")
t1 = leer_atributos_xml("elemento1", "TAG2")
print("t1: ", t1)
t2 = leer_atributos_xml("elemento1", "TAG1")
print("t2: ", t2, type(t2))
t3 = leer_atributos_xml("elemento1", "TAG1", "i")
print("t2: ", t3, type(t3))
t4 = leer_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"), 
    ("TAG4", "TAG5", "TAG6"), "sf")
print("t4: ", t4)
t5 = leer_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"), "TAG5", "f")
print("t5: ", t5, type(t5))
t6 = leer_atributos_xml(
    ("elemento1", "elemento2"), ("TAG3", "TAG7"))
print("t6: ", t6)
###########################################################################

    """
    if archivo is None:
        archivo = archivo_xml
    raiz = archivo.getroot()
    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)
    # Descendemos hasta el elemento del nivel indicado.
    for etiqueta in elementos:
        raiz = raiz.find(etiqueta)
    lista = aux_atributos_xml(raiz, atributos, formatos)
    return lista


@captura_error
def guardar_atributos_xml(elementos, atributos, valores, formatos=None):
    """
    Actualiza los atributos de un elemento, y lo guarda en el archivo xml

    """
    raiz = archivo_xml.getroot()
    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)
    # Descendemos hasta el elemento del nivel indicado.
    for etiqueta in elementos:
        raiz = raiz.find(etiqueta)

    aux_atributos_xml(raiz, atributos, formatos, valores)
    # Y finalmente guardamos el archivo.
    archivo_xml.write(nombre_xml, encoding="utf-8", xml_declaration=True)


@captura_error
def leer_lista_xml(elementos, nombre, atributo, formato="s", archivo=None):
    """
    Lee todos los elmentos con el mismo nombre dentro de otro elemento.

    Argumentos:
    - elementos: ver función leer_atributos_xml
    - nombre: nombre del elemento del cual queremos generar la lista.
    - atributo: atributo a devolver de cada elemento anterior.

###########################################################################
# Archivo prueba.xml
###########################################################################
<prueba>
    <elemento1>
        <campo TAG="1"/>
        <campo TAG="2"/>
        <campo TAG="3"/>
        <campo TAG="4"/>
        <elemento2>
            <campo TAG2="A"/>
            <campo TAG2="B"/>
            <campo TAG2="C"/>
            <campo TAG1="D"/>
        </elemento2>
    </elemento1>
</prueba>
###########################################################################

###########################################################################
# Archivo prueba.py
###########################################################################
from python_comun import abrir_archivo_xml
from python_comun import leer_lista_xml

abrir_archivo_xml("prueba.xml")
l1 = leer_lista_xml("elemento1", "campo", "TAG")
print("l1: ", l1)
l2 = leer_lista_xml("elemento1", "campo", "TAG", "i")
print("l2: ", l2)
l3 = leer_lista_xml(("elemento1", "elemento2"), "campo", "TAG2")
print("l3: ", l3)
l4 = leer_lista_xml(("elemento1", "elemento2"), "campo", "TAG1")
print("l4: ", l4)
###########################################################################


    """
    if archivo is None:
        archivo = archivo_xml

    raiz = archivo.getroot()

    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)
    # Descendemos hasta el elemento del nivel indicado.
    for etiqueta in elementos:
        raiz = raiz.find(etiqueta)

    lista = ()
    # Obtenemos todos los elementos con el nombre solicitado.
    elementos_lista = raiz.findall(nombre)
    if len(elementos_lista) == 0:
        # Si no hay ningún elemento, se trata de un error.
        raise ValueError
    for campo in elementos_lista:
        try:
            # Comprobamos si existe el tag en dicho elemento.
            valor = campo.attrib[atributo]
        except KeyError:
            continue
        # Convertimos al formato indicado.
        valor = convertir_tipo(valor, formato)
        lista += (valor,)
    return lista


@captura_error
def guardar_lista_xml(elementos, nombre, atributos, valores, formatos="s"):
    """
    Guarda una lista de elementos (ver leer_lista_xml.

    Argumentos:
    - atributos: lista de atributos que tienen TODOS los elementos.
    - valores: lista de lista de valores. La longitud de valores indica cuantos
      elementos con el mismo nombre se añaden, y la longitud de cada uno de los
      elementos de la lista anterior debe ser igual a la de atributos.

    """

    raiz = archivo_xml.getroot()
    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)
    # Descendemos hasta el elemento del nivel indicado.
    for etiqueta in elementos:
        raiz = raiz.find(etiqueta)

    # Eliminamos todos los elementos del mismo nombre.
    elementos_lista = raiz.findall(nombre)
    for elemento_lista in elementos_lista:
        raiz.remove(elemento_lista)

    # Y añadimos los nuevos elementos.
    for valores_elemento in valores:
        # Creamos un nuevo elemento donde guardar los atributos.
        nuevo_elemento = ElementTree.Element(nombre)
        aux_atributos_xml(nuevo_elemento, atributos,
                          formatos, valores_elemento)
        raiz.append(nuevo_elemento)
    # Y finalmente guardamos el archivo.
    archivo_xml.write(nombre_xml, encoding="utf-8", xml_declaration=True)


# @captura_error
def leer_lista_atributos_xml(elementos, nombre, atributos,
                             formatos=None, archivo=None):
    """
    Similar a leer_lista_xml, pero solicitando más de un atributo.

    Se devuelve una lista, donde cada elemento es un diccionario con los
    atributos solicitados. Solo se incluyen los elementos que tengan todos
    los atributos indicados. 

###########################################################################
# Archivo prueba.xml
###########################################################################
<prueba>
    <elemento1>
        <campo TAG1="1" TAG2="A"/>
        <campo TAG1="2" TAG2="B"/>
        <campo TAG1="3"/>
        <campo TAG1="4" TAG2="C"/>
        <elemento2>
            <campo TAG2="A"/>
            <campo TAG2="B"/>
            <campo TAG2="C"/>
            <campo TAG1="D"/>
        </elemento2>
    </elemento1>
</prueba>
###########################################################################

###########################################################################
# Archivo prueba.py
###########################################################################
from python_comun import abrir_archivo_xml
from python_comun import leer_lista_atributos_xml

abrir_archivo_xml("prueba.xml")
l1 = leer_lista_atributos_xml("elemento1", "campo", "TAG1")
print("l1: ", l1)
l2 = leer_lista_atributos_xml("elemento1", "campo", ("TAG1", "TAG2"))
print("l2: ", l2)
l3 = leer_lista_atributos_xml("elemento1", "campo", ("TAG1", "TAG2"), "is")
print("l3: ", l3)

l4 = leer_lista_atributos_xml(("elemento1", "elemento2"), "campo", "TAG2")
print("l4: ", l4)
l5 = leer_lista_atributos_xml( ("elemento1", "elemento2"), "campo", ("TAG2", "TAG1") )
print("l5: ", l5)


    """
    if archivo is None:
        archivo = archivo_xml
    raiz = archivo.getroot()

    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)
    # Descendemos hasta el elemento del nivel indicado.
    for etiqueta in elementos:
        raiz = raiz.find(etiqueta)

    lista = ()
    elementos_lista = raiz.findall(nombre)
    if len(elementos_lista) == 0:
        raise ValueError
    for campo in elementos_lista:
        try:
            valores = aux_atributos_xml(campo, atributos, formatos)
        except KeyError:
            continue
        lista += (valores,)
    return lista


# @captura_error
def leer_directorio_xml(elementos, tag):
    """
    Construye un directorio a partir de varios elementos anidados.

    El directorio se construye con todos los elementos que tengan el tag
    tag. Si un elmento no lo tiene, pero alguno de los elementos que
    están dentro de el sí, no es ningún error, simplemente se ignora este
    elemento y se sigue construyendo a partir de su descendiente.

    elementos es una lista de todos los elementos, en sentido descendente, que
    hay que recorrer. Por ejemplo:
###########################################################################
# Archivo prueba.xml
###########################################################################
<prueba>
    <elemento1 DIRECTORIO="dir1/">
        <elemento2 OTRO_TAG="otro">
            <elemento3 DIRECTORIO="dir3/">
                <elemento4 DIRECTORIO="dir4/">
                </elemento4>
            </elemento3>
        </elemento2>
    </elemento1>
</prueba>
###########################################################################

###########################################################################
# Archivo prueba.py
###########################################################################
from python_comun import abrir_archivo_xml
from python_comun import leer_directorio_xml
abrir_archivo_xml("prueba.xml")
var = leer_directorio_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4" ),
    "DIRECTORIO")
print("Directorio: ", var)
###########################################################################
>> dir1/dir3/dir4/

    """
    raiz = archivo_xml.getroot()
    # Comprobamos si la raíz es una lista de etiquetas:
    if not isinstance(elementos, (list, tuple)):
        elementos = (elementos,)

    # Construimos el directorio en esta variable.
    directorio = ""
    for elemento in elementos:
        # Avanzamos hasta el siguiente elemento.
        raiz = raiz.find(elemento)
        try:
            # Comprobamos si el elemento tiene el tag
            d = raiz.attrib[tag]
            # Si lo tiene, lo añadimos al directorio.
            directorio += d
        except KeyError:
            pass
    return directorio


##########################################################################


"""
###############################################################################
# Archivo prueba.xml
###############################################################################
<?xml version='1.0' encoding='utf-8'?>
<prueba>
    <elemento1 TAG1="24" TAG2="hola">
        <elemento2 TAG3="otro" TAG7="más">
            <elemento3>
                <elemento4 TAG4="prueba" TAG5="14.2" TAG6="otra">
                </elemento4>
            </elemento3>
        </elemento2>
    </elemento1>
</prueba>
###############################################################################

###############################################################################
# Archivo prueba.py
###############################################################################
abrir_archivo_xml("prueba.xml")
t1 = leer_atributos_xml("elemento1", "TAG1")
print("t1: ", t1)
guardar_atributos_xml("elemento1", "TAG1", "26")
t1 = leer_atributos_xml("elemento1", "TAG1")
print("t1: ", t1)
guardar_atributos_xml("elemento1", "TAG1", 28, "i")
t1 = leer_atributos_xml("elemento1", "TAG1")
print("t1: ", t1)
guardar_atributos_xml("elemento1", "TAG1", "24")

t2 = leer_atributos_xml("elemento1", "TAG1")
print("t2: ", t2, type(t2))
t3 = leer_atributos_xml("elemento1", "TAG1", "i")
print("t2: ", t3, type(t3))

t4 = leer_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"),
    ("TAG4", "TAG5", "TAG6"), "sf")
print("t4: ", t4)
guardar_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"),
    ("TAG4", "TAG5", "TAG6"),
    ("cambio", -4.56, "valor"), "sfs")
t4 = leer_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"),
    ("TAG4", "TAG5", "TAG6"), "sf")
print("t4: ", t4)
guardar_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"),
    ("TAG4", "TAG5", "TAG6"),
    ("prueba", "14.2", "otra"), "sfs")

t5 = leer_atributos_xml(
    ("elemento1", "elemento2", "elemento3", "elemento4"), "TAG5", "f")
print("t5: ", t5, type(t5))
t6 = leer_atributos_xml(
    ("elemento1", "elemento2"), ("TAG3", "TAG7"))
print("t6: ", t6)

guardar_lista_xml(
    ("elemento1", "elemento2", "elemento3"),
    "campo", ("TAG_A", "TAG_B"),
    (
        ("uno", "dos"),
        ("tres", "cuato")
    ))
###############################################################################
"""
