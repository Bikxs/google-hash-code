from typing import List

from utils import *


class Simulation:
    def __init__(self, rows: int, columns: int, deadline: int):
        self.rows = rows
        self.columns = columns
        self.deadline = deadline

    def __str__(self):
        return f'{self.rows}x{self.columns} {self.deadline}-seconds'


class Warehouse:
    def __init__(self, id: int, row: int, column: int, stock: List[int]):
        self.id = id
        self.row = row
        self.column = column
        self.stock = stock

    def __str__(self):
        return f'WH{self.id}({self.row},{self.column})'


class Product:
    def __init__(self, id: int, weight: int):
        self.id = id
        self.weight = weight

    def __str__(self):
        return f'P{self.id} weight: {self.weight}'


class Customer:
    def __init__(self, id: int, row: int, column: int, order_items: List[int]):
        self.id = id
        self.row = row
        self.column = column
        self.order_items = order_items

    def __str__(self):
        return f'C{self.id}({self.row},{self.column})'


class Drone:
    def __init__(self, id: int, starting_warehouse: Warehouse, max_load: int):
        self.id = id
        self.row = starting_warehouse.row
        self.column = starting_warehouse.column
        self.max = max_load

    def __str__(self):
        return f'D{self.id}({self.row},{self.column})'


class Problem:
    def __init__(self, filename: string):
        self.prefix = filename[0]
        self.filename = f"{INPUT_FOLDER}/{filename}"
        self.name = filename.replace(".in", "")

        self.warehouses = []
        self.customers = []

        i = 0
        warehouse_id = 0
        customer_id = 0
        customer_next_line = 1
        with open(self.filename, 'r') as f:
            for line in f:
                line_data = line.strip().split(' ')
                if i == 0:
                    """
                    number of rows in the area of the simulation
                    ( 1 ≤ n umber of rows ≤ 1 0000)
                    """
                    rows = int(line_data[0])
                    """
                    number of columns in the area of the simulation
                    ( 1 ≤ n umber of columns ≤ 1 0000)
                    """
                    columns = int(line_data[1])
                    """ number of drones available ( 1 ≤ D ≤ 1 000) """
                    drones = int(line_data[2])
                    """
                    deadline of the simulation
                    ( 1 ≤ d eadline of the simulation ≤ 1 000000)
                    """
                    deadline = int(line_data[3])
                    """
                    maximum load of a drone
                    ( 1 ≤ m aximum load of a drone ≤ 1 0000)
                    """
                    maximum_load = int(line_data[4])
                elif i == 1:
                    """
                    P the number of different product types available in warehouses
                    ( 1 ≤ P ≤ 1 0000)
                    """
                    products = int(line_data[0])
                elif i == 2:
                    """
                    weights of subsequent products types, from product type 0 to product type P 1. 
                    For each weight, 1 ≤ w eight ≤ m aximum load of a drone .
                    """
                    products_weights = [int(x) for x in line_data]
                elif i == 3:
                    """W - the number of warehouses ( 1 ≤ W ≤ 1 0000)"""
                    warehouses = int(line_data[0])
                    warehouse_line_start = i + 1
                    warehouse_line_end = warehouse_line_start + (warehouses * 2) - 1
                elif warehouse_line_start <= i <= warehouse_line_end:
                    if i % 2 == 0:
                        warehouse_row = int(line_data[0])
                        warehouse_column = int(line_data[1])
                    else:
                        warehouse_stock = [int(x) for x in line_data]
                        self.warehouses.append(Warehouse(warehouse_id, warehouse_row, warehouse_row, warehouse_stock))
                        warehouse_id += 1
                elif i == warehouse_line_end + 1:
                    customers = int(line_data[0])
                    customers_line_start = i + 1
                    customers_line_end = customers_line_start + (customers * 3) - 1
                elif customers_line_start <= i <= customers_line_end:
                    if customer_next_line == 1:
                        """
                        a line containing two natural numbers separated by a single space: the row of the delivery
                        cell and the column of the delivery cell
                        ( 0 ≤ r ow < number of rows; 0 ≤ c olumn < number of columns)
                        """
                        customer_row = int(line_data[0])
                        customer_column = int(line_data[1])
                        customer_next_line = 2
                    elif customer_next_line == 2:
                        """
                        a line containing one natural number Li the number of the ordered product items
                        """
                        customer_ordered_product_items_number = line_data[0]
                        customer_next_line = 3
                    elif customer_next_line == 3:
                        """
                        a line containing Li integers separated by single spaces: the product types of the individual
                        product items. For each of the product types, 0 ≤ p roduct type < P holds.
                        """
                        customer_ordered_product_items = [int(x) for x in line_data]
                        self.customers.append(
                            Customer(customer_id, customer_row, customer_column, customer_ordered_product_items))
                        customer_next_line = 1
                        customer_id += 1
                else:
                    raise Exception("Not expecting to read data")

                i += 1

        self.simulation = Simulation(rows, columns, deadline)
        self.drones = [Drone(d, self.warehouses[0], max_load=maximum_load) for d in range(drones)]
        self.products = [Product(p_id, products_weights[p_id]) for p_id in range(products)]

    def __str__(self):
        return f'{self.name.upper()}\n\tFilename: {self.filename}' \
               f'\n\tSimulation: {self.simulation}' \
               f'\n\tWarehouse: {len(self.warehouses)}' \
               f'\n\tProducts: {len(self.products)}' \
               f'\n\tDrones: {len(self.drones)}' \
               f'\n\tCustomers: {len(self.customers)}'


def read_problem(filename) -> Problem:
    return Problem(filename)
