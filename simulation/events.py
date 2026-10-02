import numpy as np
import pandas as pd

class EmpiricalEventSampler:
    """Samples simulated logistics events based on historical DataCo empirical distributions."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        
        # DataCo empirical shipping mode mix
        self.shipping_mode_probs = {
            'Standard Class': 0.60,
            'Second Class': 0.20,
            'First Class': 0.15,
            'Same Day': 0.05
        }
        
        # Mode-specific delay probabilities
        self.mode_delay_probs = {
            'First Class': 1.00,
            'Second Class': 0.798,
            'Same Day': 0.479,
            'Standard Class': 0.398
        }
        
    def sample_shipping_mode(self) -> str:
        modes = list(self.shipping_mode_probs.keys())
        probs = list(self.shipping_mode_probs.values())
        return str(self.rng.choice(modes, p=probs))
        
    def sample_is_late(self, shipping_mode: str) -> bool:
        prob = self.mode_delay_probs.get(shipping_mode, 0.40)
        return bool(self.rng.random() < prob)
        
    def sample_delay_hours(self, shipping_mode: str) -> int:
        if shipping_mode == 'First Class':
            return int(self.rng.integers(24, 72))
        elif shipping_mode == 'Second Class':
            return int(self.rng.integers(12, 48))
        else:
            return int(self.rng.integers(6, 24))
