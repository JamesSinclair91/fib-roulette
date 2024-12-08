import streamlit as st
from functools import lru_cache
from random import randint


# Memoized Fibonacci calculation
@lru_cache(None)
def fib(n):
    if n <= 2:
        return 1
    return fib(n - 1) + fib(n - 2)


# Session class and main simulation logic
class Session:
    def __init__(self, balance, unit_bet, max_bet, target_profit):
        self.start_balance = balance
        self.balance = balance
        self.unit_bet = unit_bet
        self.max_bet = 0 if max_bet is None else max_bet
        self.target_profit = target_profit
        self.current_bet = unit_bet
        self.fib_index = 1  # Start at Fibonacci index 1
        self.spins = 0
        self.wins = 0
        self.losses = 0
        self.cycle = 1

    def place_bet(self, won):
        current_fib_index = self.fib_index
        self.current_bet = self.unit_bet * fib(current_fib_index)

        if self.current_bet > self.balance:
            self.current_bet = self.balance

        if self.max_bet > 0 and self.current_bet > self.max_bet:
            self.current_bet = self.max_bet

        self.balance -= self.current_bet

        if won:
            self.balance += self.current_bet * 3
            self.fib_index = 1
            self.wins += 1
        else:
            self.fib_index += 1
            self.losses += 1

        self.spins += 1
        return current_fib_index

    def reached_target(self):
        return self.balance - self.start_balance >= self.target_profit or self.balance <= 0


def spin_roulette():
    spin_result = randint(0, 36)
    return spin_result, 25 <= spin_result <= 36


# Streamlit interface
st.title("Fibonacci Dozens Betting Simulator")

# User inputs
start_balance = st.number_input("Starting Balance", min_value=0.1, step=0.01, value=1500.00)
unit_bet = st.number_input("Unit Bet", min_value=0.1, step=0.01, value=5.00)
max_bet = st.number_input("Maximum Bet (optional)", min_value=0.0, step=0.01, value=None, placeholder="Leave blank for no max bet")
target_profit = st.number_input("Target Profit", min_value=0.0, step=0.01, value=100.00)
max_spins = st.number_input("Maximum Spins (optional)", min_value=0, step=1, value=None, format="%d", placeholder="Leave blank for infinite spins")

if st.button("Run Simulation"):
    session = Session(start_balance, unit_bet, max_bet or None, target_profit)
    results = []

    while (max_spins is None or session.spins < max_spins) and not session.reached_target():
        pre_spin_balance = session.balance
        number, win = spin_roulette()
        
        current_fib_index = session.place_bet(win)
        fib_multiplier = fib(current_fib_index)
        post_spin_balance = session.balance

        results.append({
            'spin': session.spins,
            'balance_pre_spin': pre_spin_balance,
            'cycle': session.cycle,
            'fib_index': current_fib_index,
            'fib_multiplier': fib_multiplier,
            'current_bet': session.current_bet,
            'number': number,
            'won_or_lost': "Won" if win else "Lost",
            'winnings': post_spin_balance - pre_spin_balance + session.current_bet if win else "",
            'balance_post_spin': post_spin_balance,
            'profit': post_spin_balance - session.start_balance,
            'profit_pct': "{:.2%}".format((post_spin_balance / session.start_balance) - 1),
            'wins': session.wins,
            'losses': session.losses,
            'win_pct': "{:.2%}".format(session.wins / session.spins),
            'loss_pct': "{:.2%}".format(session.losses / session.spins)
        })

        session.cycle += 1 if win else 0

    stats = {
        'result': session.balance - session.start_balance,
        'total_spins': session.spins,
        'win_pct': f"{session.wins / session.spins:.2%}" if session.spins > 0 else "0%",
        'largest_bet': max(r['current_bet'] for r in results),
        'largest_fib_index': max(r['fib_index'] for r in results),
    }

    # Display results
    st.subheader("Simulation Results")
    st.dataframe(stats)

    st.subheader("Detailed Spin Results")
    st.dataframe(results)
