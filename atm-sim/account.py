
from datetime import datetime


class Account:
    """Represents a demo ATM bank account."""

    def __init__(
        self,
        holder_name="Prabin Mandal",
        account_number="123456789012",
        card_number="4567 1234 5678 9012",
        pin="1234",
        balance=25000.00,
    ):
        self.holder_name = holder_name
        self.account_number = account_number
        self.card_number = card_number
        self._pin = str(pin).strip()
        self.balance = float(balance)
        self.transactions = []

        self._add_transaction(
            "Account Opened", 0, "Account initialized"
        )

    # --------------------------------------------------
    # ACCOUNT DETAILS
    # --------------------------------------------------

    def get_account_details(self):
        return {
            "holder_name": self.holder_name,
            "account_number": self.account_number,
            "card_number": self.card_number,
            "balance": self.balance,
        }

    def get_masked_account_number(self):
        return f"****{self.account_number[-4:]}"

    def get_masked_card_number(self):
        digits = "".join(
            char for char in self.card_number
            if char.isdigit()
        )
        return f"**** **** **** {digits[-4:]}"

    # --------------------------------------------------
    # PIN VERIFICATION
    # --------------------------------------------------

    def verify_pin(self, entered_pin):
        """Return True only when the supplied PIN is correct."""
        return str(entered_pin).strip() == self._pin

    # --------------------------------------------------
    # PIN MANAGEMENT
    # --------------------------------------------------

    def change_pin(self, current_pin, new_pin, confirm_pin):
        """Change the PIN after verifying the current PIN."""

        current_pin = str(current_pin).strip()
        new_pin = str(new_pin).strip()
        confirm_pin = str(confirm_pin).strip()

        if not self.verify_pin(current_pin):
            return False, "Incorrect current PIN."

        if not new_pin.isdigit() or len(new_pin) != 4:
            return False, "The new PIN must contain exactly 4 digits."

        if new_pin == current_pin:
            return False, "The new PIN must differ from the current PIN."

        if new_pin != confirm_pin:
            return False, "The new PIN and confirmation do not match."

        self._pin = new_pin

        self._add_transaction(
            "PIN Changed", 0, "ATM PIN updated"
        )

        return True, "PIN changed successfully."

    # --------------------------------------------------
    # BALANCE
    # --------------------------------------------------

    def check_balance(self):
        return self.balance

    # --------------------------------------------------
    # WITHDRAWAL
    # --------------------------------------------------

    def withdraw(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Please enter a valid withdrawal amount."

        if amount <= 0:
            return False, "Withdrawal amount must be greater than zero."

        if not amount.is_integer():
            return False, "Enter a whole-number amount."

        amount = int(amount)

        if amount % 100 != 0:
            return False, "Withdrawal amount must be in multiples of ₹100."

        if amount > self.balance:
            return False, "Insufficient account balance."

        # Change the balance only after every validation passes.
        self.balance -= amount

        self._add_transaction(
            "Withdrawal",
            -amount,
            "ATM cash withdrawal",
        )

        return True, f"Please collect your ₹{amount:,} cash."

    # --------------------------------------------------
    # DEPOSIT
    # --------------------------------------------------

    def deposit(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Please enter a valid deposit amount."

        if amount <= 0:
            return False, "Deposit amount must be greater than zero."

        if not amount.is_integer():
            return False, "Enter a whole-number amount."

        amount = int(amount)
        self.balance += amount

        self._add_transaction(
            "Deposit", amount, "Cash deposit"
        )

        return True, f"₹{amount:,} deposited successfully."

    # --------------------------------------------------
    # TRANSACTION HISTORY
    # --------------------------------------------------

    def _add_transaction(
        self, transaction_type, amount, description=""
    ):
        now = datetime.now()

        self.transactions.append({
            "date": now.strftime("%d-%m-%Y"),
            "time": now.strftime("%I:%M:%S %p"),
            "type": transaction_type,
            "amount": float(amount),
            "balance": self.balance,
            "description": description,
        })

    def get_mini_statement(self, limit=5):
        try:
            limit = max(0, int(limit))
        except (TypeError, ValueError):
            limit = 5

        if limit == 0:
            return []

        return list(reversed(self.transactions[-limit:]))

    def format_mini_statement(self, limit=5):
        transactions = self.get_mini_statement(limit)

        if not transactions:
            return "No transactions available."

        lines = [
            f"MINI STATEMENT - {self.holder_name}",
            f"Account: {self.get_masked_account_number()}",
            "-" * 42,
        ]

        for transaction in transactions:
            amount = transaction["amount"]

            if amount > 0:
                amount_text = f"+₹{amount:,.2f}"
            elif amount < 0:
                amount_text = f"-₹{abs(amount):,.2f}"
            else:
                amount_text = "₹0.00"

            lines.extend([
                f'{transaction["date"]} {transaction["time"]}',
                f'{transaction["type"]}: {amount_text}',
                f'Balance: ₹{transaction["balance"]:,.2f}',
                "-" * 42,
            ])

        return "\n".join(lines)

    # --------------------------------------------------
    # DEMO ATM COMPATIBILITY
    # --------------------------------------------------

    def mini_statement(self, limit=5):
        """Return entries compatible with the existing main.py."""

        return [
            (
                transaction["date"],
                transaction["description"] or transaction["type"],
                transaction["amount"],
            )
            for transaction in self.get_mini_statement(limit)
        ]


class DemoAccount(Account):
    """Adapter for the existing StarkATM application."""

    def withdraw(self, amount):
        success, message = super().withdraw(amount)

        if not success:
            raise ValueError(message)

        return message

    def change_pin(self, new_pin):
        """Maintain compatibility with main.py's change_pin(new_pin)."""

        new_pin = str(new_pin).strip()

        if not new_pin.isdigit() or len(new_pin) != 4:
            raise ValueError(
                "The new PIN must contain exactly 4 digits."
            )

        if new_pin == self._pin:
            raise ValueError(
                "The new PIN must be different from the current PIN."
            )

        self._pin = new_pin

        self._add_transaction(
            "PIN Changed", 0, "ATM PIN updated"
        )

        return True


# --------------------------------------------------
# SHARED DEMO ACCOUNT
# --------------------------------------------------

demo_account = DemoAccount(
    holder_name="Prabin Mandal",
    account_number="123456789012",
    card_number="4567 1234 5678 9012",
    pin="1234",
    balance=25000.00,
)


# --------------------------------------------------
# ACCOUNT TEST
# --------------------------------------------------

if __name__ == "__main__":
    account = DemoAccount()

    print("STARK ATM ACCOUNT TEST")
    print("-" * 35)
    print("Holder:", account.holder_name)
    print("Account:", account.get_masked_account_number())
    print(f"Balance: ₹{account.check_balance():,.2f}")

    print("\nPIN verification:", account.verify_pin("1234"))

    try:
        print("\nWithdrawal:", account.withdraw(500))
    except ValueError as exc:
        print("\nWithdrawal failed:", exc)

    print(f"Balance after withdrawal: ₹{account.check_balance():,.2f}")
    print()
    print(account.format_mini_statement())
