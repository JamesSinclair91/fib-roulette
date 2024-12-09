import streamlit as st
import pandas as pd
#from  scipy import stats
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
        self.largest_fib_index = 1
        self.largest_multiplier = 1
        self.spins = 0
        self.wins = 0
        self.losses = 0
        self.cycle = 1

    def place_bet(self, won):
        # Sets the current fib index
        current_fib_index = self.fib_index
        
        # Ensures the largest fib index of the session is tracked
        if current_fib_index > self.largest_fib_index:
            self.largest_fib_index = current_fib_index
            self.largest_fib_multiplier = fib(current_fib_index)

        # Sets the current bet
        self.current_bet = self.unit_bet * fib(current_fib_index)

        
        # Check if you can make the current bet, otherwise bet the remaining balance
        #self.current_bet = min(self.current_bet, self.balance)
        
        # Only bet up to the maximum bet
        #if self.max_bet > 0 and self.current_bet > self.max_bet:
        #    self.current_bet = self.max_bet

        # Check if you can make the current bet, otherwise bet the remaining balance
        self.current_bet = min(self.current_bet, self.balance, self.max_bet)


        # By placing the bet, balances reduces
        self.balance -= self.current_bet

        # On a win you get 3x your bet, the fib index resets to 1, and number of wins is incremented
        if won:
            self.balance += self.current_bet * 3
            self.fib_index = 1
            self.wins += 1
        
        # On a loss, the fib index and number of losses is incremented
        else:
            self.fib_index += 1
            self.losses += 1

        # Regardles of outcome, the number of spins increments.
        self.spins += 1
        
        return current_fib_index

    # Dynamic profit calculation
    @property
    def actual_profit(self):
        return self.balance - self.start_balance
    
    # End the session if profit exceeds target or balance is 0
    def reached_target(self):
        #return self.balance - self.start_balance >= self.target_profit or self.balance <= 0
        return self.actual_profit >= self.target_profit or self.balance <= 0


def spin_roulette():
    spin_result = randint(0, 36)
    return spin_result, 25 <= spin_result <= 36


# Streamlit interface
st.title("Fibonacci Dozens Betting Simulator")

# User inputs
start_balance = st.number_input("Starting Balance", 
                                min_value=0.01, 
                                step=0.01, 
                                value=1500.00,
                                format="%.2f",
                                placeholder="Enter a starting balance"
                                )
unit_bet = st.number_input("Unit Bet", 
                                min_value=0.01, 
                                step=0.01, 
                                value=5.00,
                                format="%.2f",
                                placeholder="Enter a unit bet"
                                )
max_bet = st.number_input("Maximum Bet (optional)",
                                min_value=0.0, 
                                step=0.01, 
                                value=None,
                                format="%.2f", 
                                placeholder="Leave blank for no max bet"
                                )
target_profit = st.number_input("Target Profit", 
                                min_value=0.0, 
                                step=0.01, 
                                value=100.00,
                                format="%.2f",
                                placeholder="Enter a profit target (£)"
                                )
max_spins = st.number_input("Maximum Spins (optional)", 
                                min_value=1, 
                                step=1, 
                                value=None, 
                                format="%d", 
                                placeholder="Leave blank for infinite spins"
                                )

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
            'winnings': post_spin_balance - pre_spin_balance + session.current_bet if win else 0,
            'balance_post_spin': post_spin_balance,
            'profit': post_spin_balance - session.start_balance,
            'profit_pct': (post_spin_balance / session.start_balance) - 1,
            'wins': session.wins,
            'losses': session.losses,
            'win_pct': session.wins / session.spins,
            'loss_pct': session.losses / session.spins
        })

        session.cycle += 1 if win else 0

    # Check to see if integers or floats should be used
    use_integer = True if session.start_balance % 1 == 0 and session.unit_bet % 1 == 0 else False

    def format_number(value):
        return f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}"

    
    # Formatted stats
    stats_target_amount = format_number(session.target_profit)
    stats_target_pct = "{:.2%}".format(session.target_profit / session.start_balance)
    stats_target_units = format_number(session.target_profit / session.unit_bet)

    stats_result_amount = format_number(session.actual_profit)
    stats_result_pct = "{:.2%}".format(session.actual_profit / session.start_balance)
    stats_result_units = format_number(session.actual_profit / session.unit_bet)

    stats_total_spins = "{:,.0f}".format(session.spins)
    stats_wins = "{:,.0f}".format(session.wins)
    stats_win_pct = "{:.2%}".format(session.wins / session.spins)
    stats_cycles = "{:,.0f}".format(session.wins + (0 if results[-1]['won_or_lost'] == "Won" else 1))
    stats_losses = "{:,.0f}".format(session.losses)
    
    stats_fib_index = "{:,.0f}".format(session.largest_fib_index)
    stats_largest_multiplier = "{:,.0f}".format(session.largest_fib_multiplier)
    stats_largest_bet = format_number(session.largest_fib_multiplier * session.unit_bet)
    stats_odds = "{:.2%}".format((25 / 37) ** session.largest_fib_index)

    # Display results
    st.subheader("Simulation Results")
    
    st.text(f"""
            Target: £{stats_target_amount} ({stats_target_pct}) ({stats_target_units} units)
            Result: £{stats_result_amount} ({stats_result_pct}) ({stats_result_units} units)
            
            Total Spins: {stats_total_spins} (Wins: {stats_wins} / Losses: {stats_losses})
            Cycles: {stats_cycles}
            Win Rate: {stats_win_pct}     (vs expected 32.43%)
            This simulation won Only xxx% of all scenarios outperformed this one
            
            Largest Bet: £{stats_largest_bet} (Index: {stats_fib_index} / Multipler: {stats_largest_multiplier}x)
            Odds on largest Fib Index: {stats_odds}
            """)
    
 
    st.subheader("Detailed Spin Results")
    results_table = pd.DataFrame(results)
    st.dataframe(results_table, hide_index=True, use_container_width=False)


# To Add:
# Add Profit graph (0 is bold line)
# Add binom distribution to stats
# Format: balances / current bet / winnings / profit
# Wheel number colours
# Bold where Fib index = 1
# Alternate red and blue for cycles
# Winnings "" where nil
# Profit column heatmap
# Win/Loss %s
# Checkbox to switch between units

