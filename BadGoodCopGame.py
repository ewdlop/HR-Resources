import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from typing import Dict, Tuple, List

class BadGoodCopGame:
    def __init__(self):
        # Game parameters
        self.confession_value = 10.0     # Value of getting a confession
        self.intimidation_cost = 2.0     # Cost of intimidation tactics
        self.rapport_cost = 1.0          # Cost of building rapport
        self.suspect_resistance = 5.0    # Base suspect resistance level
        
    def create_payoff_matrix(self) -> Dict[str, np.ndarray]:
        """Create payoff matrices for different strategies."""
        
        # Strategy space:
        # Cops: [Aggressive, Friendly, Neutral]
        # Suspect: [Confess, Resist]
        
        # Bad cop payoff matrix
        bad_cop_payoff = np.array([
            # Confess  Resist
            [self.confession_value - self.intimidation_cost,   -self.intimidation_cost],  # Aggressive
            [self.confession_value * 0.3 - self.rapport_cost,  -self.rapport_cost],       # Friendly
            [self.confession_value * 0.1,                      0]                         # Neutral
        ])
        
        # Good cop payoff matrix
        good_cop_payoff = np.array([
            # Confess  Resist
            [self.confession_value * 0.2 - self.intimidation_cost, -self.intimidation_cost],  # Aggressive
            [self.confession_value - self.rapport_cost,            -self.rapport_cost],        # Friendly
            [self.confession_value * 0.3,                          0]                          # Neutral
        ])
        
        # Suspect payoff matrix against bad cop
        suspect_vs_bad = np.array([
            # Aggressive  Friendly  Neutral
            [-8, -2, -1],  # Confess
            [-5,  0,  2]   # Resist
        ])
        
        # Suspect payoff matrix against good cop
        suspect_vs_good = np.array([
            # Aggressive  Friendly  Neutral
            [-4, -1, -1],  # Confess
            [-2,  1,  2]   # Resist
        ])
        
        return {
            'bad_cop': bad_cop_payoff,
            'good_cop': good_cop_payoff,
            'suspect_vs_bad': suspect_vs_bad,
            'suspect_vs_good': suspect_vs_good
        }

    def calculate_nash_equilibrium(self, payoff_matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """Calculate Nash equilibrium strategies."""
        num_strategies = payoff_matrix.shape[0]
        
        def objective(x):
            strategies = x[:num_strategies]
            strategies = strategies / np.sum(strategies)
            return -np.min(np.dot(payoff_matrix, strategies))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x[:num_strategies]) - 1}
        ]
        bounds = [(0, 1) for _ in range(num_strategies)]
        
        x0 = np.ones(num_strategies) / num_strategies
        result = minimize(objective, x0, method='SLSQP', 
                        constraints=constraints, bounds=bounds)
        
        return result.x / np.sum(result.x), -result.fun

    def simulate_interrogation(self, 
                             num_rounds: int = 10, 
                             learning_rate: float = 0.1) -> List[Dict]:
        """Simulate interrogation with learning behaviors."""
        payoffs = self.create_payoff_matrix()
        
        # Initial strategies (uniform distribution)
        bad_cop_strategy = np.array([1/3, 1/3, 1/3])
        good_cop_strategy = np.array([1/3, 1/3, 1/3])
        suspect_strategy = np.array([0.5, 0.5])
        
        history = []
        
        for round in range(num_rounds):
            # Calculate expected payoffs
            bad_cop_payoff = np.dot(payoffs['bad_cop'], suspect_strategy)
            good_cop_payoff = np.dot(payoffs['good_cop'], suspect_strategy)
            suspect_vs_bad_payoff = np.dot(payoffs['suspect_vs_bad'], bad_cop_strategy)
            suspect_vs_good_payoff = np.dot(payoffs['suspect_vs_good'], good_cop_strategy)
            
            # Record state
            history.append({
                'round': round,
                'bad_cop_strategy': bad_cop_strategy.copy(),
                'good_cop_strategy': good_cop_strategy.copy(),
                'suspect_strategy': suspect_strategy.copy(),
                'bad_cop_payoff': np.dot(bad_cop_strategy, bad_cop_payoff),
                'good_cop_payoff': np.dot(good_cop_strategy, good_cop_payoff),
                'suspect_payoff': (np.dot(suspect_strategy, suspect_vs_bad_payoff) +
                                 np.dot(suspect_strategy, suspect_vs_good_payoff)) / 2
            })
            
            # Update strategies using reinforcement learning
            bad_cop_strategy = self._update_strategy(bad_cop_strategy, bad_cop_payoff, learning_rate)
            good_cop_strategy = self._update_strategy(good_cop_strategy, good_cop_payoff, learning_rate)
            suspect_payoff = (suspect_vs_bad_payoff + suspect_vs_good_payoff) / 2
            suspect_strategy = self._update_strategy(suspect_strategy, suspect_payoff, learning_rate)
            
        return history

    def _update_strategy(self, strategy: np.ndarray, payoffs: np.ndarray, learning_rate: float) -> np.ndarray:
        """Update strategy using reinforcement learning."""
        new_strategy = strategy * (1 + learning_rate * (payoffs - np.mean(payoffs)))
        return new_strategy / np.sum(new_strategy)

    def plot_simulation_results(self, history: List[Dict]):
        """Plot simulation results."""
        rounds = [h['round'] for h in history]
        
        # Create subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
        
        # Plot strategies
        ax1.plot(rounds, [h['bad_cop_strategy'][0] for h in history], 'r-', label='Bad Cop Aggressive')
        ax1.plot(rounds, [h['bad_cop_strategy'][1] for h in history], 'b-', label='Bad Cop Friendly')
        ax1.plot(rounds, [h['bad_cop_strategy'][2] for h in history], 'g-', label='Bad Cop Neutral')
        ax1.plot(rounds, [h['good_cop_strategy'][0] for h in history], 'r--', label='Good Cop Aggressive')
        ax1.plot(rounds, [h['good_cop_strategy'][1] for h in history], 'b--', label='Good Cop Friendly')
        ax1.plot(rounds, [h['good_cop_strategy'][2] for h in history], 'g--', label='Good Cop Neutral')
        ax1.set_title('Strategy Evolution')
        ax1.set_xlabel('Round')
        ax1.set_ylabel('Strategy Probability')
        ax1.legend()
        ax1.grid(True)
        
        # Plot suspect strategies
        ax2.plot(rounds, [h['suspect_strategy'][0] for h in history], 'b-', label='Confess')
        ax2.plot(rounds, [h['suspect_strategy'][1] for h in history], 'r-', label='Resist')
        ax2.set_title('Suspect Strategy Evolution')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Strategy Probability')
        ax2.legend()
        ax2.grid(True)
        
        # Plot payoffs
        ax3.plot(rounds, [h['bad_cop_payoff'] for h in history], 'r-', label='Bad Cop')
        ax3.plot(rounds, [h['good_cop_payoff'] for h in history], 'b-', label='Good Cop')
        ax3.plot(rounds, [h['suspect_payoff'] for h in history], 'g-', label='Suspect')
        ax3.set_title('Payoff Evolution')
        ax3.set_xlabel('Round')
        ax3.set_ylabel('Payoff')
        ax3.legend()
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    game = BadGoodCopGame()
    
    # Calculate Nash equilibrium
    payoffs = game.create_payoff_matrix()
    bad_cop_eq, bad_cop_value = game.calculate_nash_equilibrium(payoffs['bad_cop'])
    good_cop_eq, good_cop_value = game.calculate_nash_equilibrium(payoffs['good_cop'])
    
    print("Nash Equilibrium Strategies:")
    print(f"Bad Cop: {bad_cop_eq}")
    print(f"Good Cop: {good_cop_eq}")
    print(f"Bad Cop Value: {bad_cop_value}")
    print(f"Good Cop Value: {good_cop_value}")
    
    # Run simulation
    history = game.simulate_interrogation(num_rounds=50, learning_rate=0.1)
    game.plot_simulation_results(history)
