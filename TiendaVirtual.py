from datetime import datetime

class Producto:
    def __init__(self, id, nombre, precio, stock):
        if precio < 0:
            raise ValueError("El precio no debe ser negativo.")
        if stock < 0:
            raise ValueError("El stock no debe ser negativo.")
        self.id = id
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)

class Inventario:
    def __init__(self, productos):
        self._productos = {p.id: p for p in productos}

    def listar(self):
        return [self._productos[k] for k in sorted(self._productos.keys())]

    def obtener(self, id_producto):
        return self._productos.get(id_producto)

    def disminuir_stock(self, id_producto, cantidad):
        prod = self.obtener(id_producto)
        if not prod:
            raise ValueError("Producto no existe.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")
        if prod.stock < cantidad:
            raise ValueError("Stock insuficiente.")
        prod.stock -= cantidad

class ItemCarrito:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = int(cantidad)

    def subtotal(self):
        return self.cantidad * self.producto.precio

class Carrito:
    def __init__(self):
        self._items = {}

    def cantidad_en_carrito(self, id_producto):
        item = self._items.get(id_producto)
        return item.cantidad if item else 0

    def agregar(self, producto, cantidad, disponible):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")
        if cantidad > disponible:
            raise ValueError("No puede agregar {}. Disponible: {}.".format(cantidad, disponible))
        if producto.id in self._items:
            self._items[producto.id].cantidad += cantidad
        else:
            self._items[producto.id] = ItemCarrito(producto, cantidad)

    def vaciar(self):
        self._items.clear()

    def esta_vacio(self):
        return len(self._items) == 0

    def total(self):
        return sum(item.subtotal() for item in self._items.values())

    def items(self):
        return [self._items[k] for k in sorted(self._items.keys())]

class Tienda:
    def __init__(self, inventario):
        self.inventario = inventario
        self.carrito = Carrito()
        self.ventas = [] 

    def _leer_int(self, msg, minimo=None):
        while True:
            entrada = input(msg).strip()
            try:
                valor = int(entrada)
                if minimo is not None and valor < minimo:
                    print("Ingrese un número entero >= {}.".format(minimo))
                    continue
                return valor
            except ValueError:
                print("Entrada inválida. Ingrese un número entero.")

    def _leer_opcion(self, msg, opciones_validas):
        op_set = set(o.lower() for o in opciones_validas)
        while True:
            op = input(msg).strip().lower()
            if op in op_set:
                return op
            print("Opción inválida. Use: {}.".format(", ".join(opciones_validas)))

    # --------- Funcionalidades del menú ---------
    def ver_productos(self):
        print("\n=== PRODUCTOS DISPONIBLES EN TIENDA ===")
        print("{:<5}{:<30}{:>10}{:>10}".format("ID", "Producto", "Precio", "Stock"))
        print("-"*60)
        for p in self.inventario.listar():
            estado = "AGOTADO" if p.stock == 0 else ""
            print("{:<5}{:<30}S/ {:>7.2f}{:>10} {}".format(p.id, p.nombre, p.precio, p.stock, estado))
        print()

    def agregar_al_carrito(self):
        print("\n=== AGREGAR AL CARRITO DE COMPRA ===")
        id_prod = self._leer_int("Ingrese ID del producto: ", minimo=1)
        prod = self.inventario.obtener(id_prod)
        if not prod:
            print("El producto no existe.")
            return
        # disponible = stock actual - cantidad ya en carrito
        ya_en_carrito = self.carrito.cantidad_en_carrito(prod.id)
        disponible = max(0, prod.stock - ya_en_carrito)
        if disponible == 0:
            print("No hay stock disponible.")
            return
        cantidad = self._leer_int("Ingrese cantidad (disponible: {}): ".format(disponible), minimo=1)
        try:
            self.carrito.agregar(prod, cantidad, disponible)
            print("Agregado: {} x {}.".format(prod.nombre, cantidad))
        except ValueError as e:
            print("X {}".format(e))

    def ver_carrito(self):
        print("\n=== CARRITO ===")
        if self.carrito.esta_vacio():
            print("El carrito está vacío.\n")
            return
        print("{:<5}{:<30}{:>7}{:>10}{:>12}".format("ID", "Producto", "Cant.", "Precio", "Subtotal"))
        print("-"*70)
        for item in self.carrito.items():
            p = item.producto
            print("{:<5}{:<30}{:>7}S/ {:>7.2f}S/ {:>9.2f}".format(p.id, p.nombre, item.cantidad, p.precio, item.subtotal()))
        print("-"*70)
        print("{:>56}  S/ {:>9.2f}\n".format("TOTAL", self.carrito.total()))

    def finalizar_compra(self):
        if self.carrito.esta_vacio():
            print("\nNo hay items en el carrito.\n")
            return
        self.ver_carrito()
        op = self._leer_opcion("¿Confirmar compra? (s/n): ", ["s", "n"])
        if op == "n":
            print("Operación cancelada.\n")
            return
        
        try:
            for item in self.carrito.items():
                self.inventario.disminuir_stock(item.producto.id, item.cantidad)
        except ValueError as e:
            print("Error al procesar compra: {}".format(e))
            print("Sugerencia: revise stock disponible o modifique el carrito.\n")
            return

        venta_items = [(it.producto.id, it.producto.nombre, it.cantidad, it.producto.precio) for it in self.carrito.items()]
        venta_total = self.carrito.total()
        venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": venta_items,
            "total": venta_total,
        }
        self.ventas.append(venta)

        print("\nCOMPROBANTE")
        print("Fecha: {}".format(venta["fecha"]))
        for pid, nombre, cant, precio in venta["items"]:
            print("- {} x{} a  S/ {:.2f}".format(nombre, cant, precio))
        print("TOTAL: S/ {:.2f}".format(venta["total"]))
        print("¡Compra realizada con éxito!\n")

        self.carrito.vaciar()

    def ejecutar(self):
        while True:
            print("===== TIENDA VIRTUAL =====")
            print("1) Ver productos disponibles")
            print("2) Agregar productos al carrito")
            print("3) Ver contenido del carrito")
            print("4) Finalizar compra")
            print("5) Salir")
            opcion = self._leer_int("Seleccione una opción (1-5): ", minimo=1)

            if opcion == 1:
                self.ver_productos()
            elif opcion == 2:
                self.agregar_al_carrito()
            elif opcion == 3:
                self.ver_carrito()
            elif opcion == 4:
                self.finalizar_compra()
            elif opcion == 5:
                print("Gracias por su compra.")
                break
            else:
                print("Opción inválida. Elija entre 1 y 5.\n")

def seed_inventario():
    productos = [
        Producto(1, "Teclado Mecánico", 149.90, 10),
        Producto(2, "Mouse Inalámbrico", 79.50, 15),
        Producto(3, "Monitor 24\" FHD", 699.00, 5),
        Producto(4, "Auriculares Bluetooth", 199.90, 8),
        Producto(5, "SSD 1TB NVMe", 329.00, 12),
    ]
    return Inventario(productos)

if __name__ == "__main__":
    tienda = Tienda(seed_inventario())
    tienda.ejecutar()
