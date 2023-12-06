import unittest
import torch
import torch.optim as optim
from helpers.training.custom_schedule import (
    get_polynomial_decay_schedule_with_warmup,
    enforce_zero_terminal_snr,
    patch_scheduler_betas,
)

class TestPolynomialDecayWithWarmup(unittest.TestCase):

    def test_polynomial_decay_schedule_with_warmup(self):
        optimizer = optim.SGD([torch.randn(2, 2, requires_grad=True)], lr=0.1)
        scheduler = get_polynomial_decay_schedule_with_warmup(
            optimizer, num_warmup_steps=10, num_training_steps=100
        )

        # Test warmup
        ranges = [0, 0.01, 0.02, 0.03, 0.04, 0.05]
        first_lr = round(scheduler.get_last_lr()[0], 2)
        for step in range(len(ranges)):
            last_lr = round(scheduler.get_last_lr()[0], 2)
            optimizer.step()
            scheduler.step()
        self.assertAlmostEqual(
            last_lr, ranges[-1], places=3
        )

        # Test decay
        for step in range(len(ranges), 100):
            optimizer.step()
            scheduler.step()
        # Implement your decay formula here to check
        expected_lr = 1e-7  
        self.assertAlmostEqual(
            scheduler.get_last_lr()[0], expected_lr, places=4
        )

    def test_enforce_zero_terminal_snr(self):
        betas = torch.tensor([0.9, 0.8, 0.7])
        new_betas = enforce_zero_terminal_snr(betas)
        final_beta = new_betas[-1]
        self.assertEqual(final_beta, 1.0)

    def test_patch_scheduler_betas(self):
        # Create a dummy scheduler with betas attribute
        class DummyScheduler:
            def __init__(self):
                self.betas = torch.tensor([0.9, 0.8, 0.7])

        scheduler = DummyScheduler()
        # Check value before.
        final_beta = scheduler.betas[-1]
        self.assertEqual(final_beta, 0.7)

        patch_scheduler_betas(scheduler)

        final_beta = scheduler.betas[-1]
        self.assertEqual(final_beta, 1.0)
        

if __name__ == "__main__":
    unittest.main()
