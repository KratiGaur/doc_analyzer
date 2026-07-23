from backend.utils.phi_masker import mask_phi

sample_text = """
Patient Name: Krati
Phone: 9876543210
Email: krati123@gmail.com
Aadhaar: 123456789012
"""

masked_text = mask_phi(sample_text)

print(masked_text)
