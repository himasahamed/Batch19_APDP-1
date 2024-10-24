class Order:
    item =[]
    quantities =[]
    price =[]
    status ="open"

    def add_item(self, name, quantity, price):
        self.item.append(name)
        self.quantities.append(quantity)
        self.price.append(price)

    def total_price(self):
        total = 0;
        for i in range(len(self.price)):
            total += self.quantities[i] * self.price[i]
        return total

    def pay (self, payment_type, security_code):

        if payment_type == "debit":
            print("processing debit payment")
            print(f"verifying security code: {security_code}")
            self.status= "paid"

        elif payment_type == "credit":
            print("processing credit payment")
            print(f"verifying security code: {security_code}")
            self.status = "paid"

        else:
            raise Exception(f"Unknown payment type: {payment_type}")

order = Order()
order.add_item("Keyboard", 1, 50)
order.add_item("SSD", 1, 150)
order.add_item("USB cable", 2, 5)

print(order.total_price())
order.pay("debit", "123495")







