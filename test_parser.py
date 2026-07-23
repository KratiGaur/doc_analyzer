from backend.utils.phi_masker import mask_phi

sample_text = """
Patient Name: John Doe
Date of Birth: 01/01/2000
Phone: 9876543210
Email: IhC6V@example.com
Aadhaar: 123456789012
"""

masked_text = mask_phi(sample_text)

print(masked_text)
