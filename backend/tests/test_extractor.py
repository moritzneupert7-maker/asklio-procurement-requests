"""Tests for the extractor.py monetary value parsing validators."""
from decimal import Decimal
import pytest
from app.services.extractor import ExtractedOrderLine, OfferExtraction


class TestMonetaryValueValidators:
    """Test the clean_monetary_value validators in ExtractedOrderLine and OfferExtraction."""

    def test_extracted_order_line_with_currency_symbols(self):
        """Test that currency symbols are properly stripped from unit_price and total_price."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price="€150.00",
            amount=1,
            unit="pcs",
            total_price="$999.99"
        )
        assert line.unit_price == Decimal("150.00")
        assert line.total_price == Decimal("999.99")

    def test_extracted_order_line_with_currency_text(self):
        """Test that currency text (EUR, USD, etc.) is properly stripped."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price="500.00 EUR",
            amount=1,
            unit="pcs",
            total_price="1000.50 USD"
        )
        assert line.unit_price == Decimal("500.00")
        assert line.total_price == Decimal("1000.50")

    def test_extracted_order_line_european_format_with_both_separators(self):
        """Test European number format: 1.767,26 → 1767.26."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price="1.767,26",
            amount=1,
            unit="pcs",
            total_price="€1.767,26"
        )
        assert line.unit_price == Decimal("1767.26")
        assert line.total_price == Decimal("1767.26")

    def test_extracted_order_line_european_format_comma_only(self):
        """Test European comma-only decimal: 150,00 → 150.00."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price="150,00",
            amount=1,
            unit="pcs",
            total_price="€999,99"
        )
        assert line.unit_price == Decimal("150.00")
        assert line.total_price == Decimal("999.99")

    def test_extracted_order_line_clean_numbers(self):
        """Test that already-clean numbers pass through unchanged."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price="150.00",
            amount=1,
            unit="pcs",
            total_price="999.99"
        )
        assert line.unit_price == Decimal("150.00")
        assert line.total_price == Decimal("999.99")

    def test_extracted_order_line_numeric_types(self):
        """Test that int and float types pass through unchanged."""
        line = ExtractedOrderLine(
            product="Test Product",
            description="Test Description",
            unit_price=150,
            amount=1,
            unit="pcs",
            total_price=999.99
        )
        assert line.unit_price == Decimal("150")
        assert line.total_price == Decimal("999.99")

    def test_offer_extraction_total_cost_with_currency(self):
        """Test that total_cost validator handles currency symbols."""
        extraction = OfferExtraction(
            title="Test Offer",
            vendor_name="Test Vendor",
            vendor_vat_id="DE123456789",
            order_lines=[
                ExtractedOrderLine(
                    product="Product 1",
                    description="Description 1",
                    unit_price="100.00",
                    amount=1,
                    unit="pcs",
                    total_price="100.00"
                )
            ],
            total_cost="€1.767,26"
        )
        assert extraction.total_cost == Decimal("1767.26")

    def test_offer_extraction_total_cost_with_currency_text(self):
        """Test that total_cost validator handles currency text."""
        extraction = OfferExtraction(
            title="Test Offer",
            vendor_name="Test Vendor",
            vendor_vat_id=None,
            order_lines=[
                ExtractedOrderLine(
                    product="Product 1",
                    description="Description 1",
                    unit_price="100.00",
                    amount=1,
                    unit="pcs",
                    total_price="100.00"
                )
            ],
            total_cost="500.00 EUR"
        )
        assert extraction.total_cost == Decimal("500.00")

    def test_offer_extraction_total_cost_comma_decimal(self):
        """Test that total_cost validator handles comma decimals."""
        extraction = OfferExtraction(
            title="Test Offer",
            vendor_name="Test Vendor",
            vendor_vat_id=None,
            order_lines=[
                ExtractedOrderLine(
                    product="Product 1",
                    description="Description 1",
                    unit_price="100.00",
                    amount=1,
                    unit="pcs",
                    total_price="100.00"
                )
            ],
            total_cost="150,00"
        )
        assert extraction.total_cost == Decimal("150.00")

    def test_complex_mixed_formats(self):
        """Test a realistic scenario with mixed European and currency formats."""
        extraction = OfferExtraction(
            title="Office Supplies",
            vendor_name="German Vendor GmbH",
            vendor_vat_id="DE198570491",
            order_lines=[
                ExtractedOrderLine(
                    product="Product 1",
                    description="Description 1",
                    unit_price="€1.234,56",
                    amount=2,
                    unit="pcs",
                    total_price="2.469,12 EUR"
                ),
                ExtractedOrderLine(
                    product="Product 2",
                    description="Description 2",
                    unit_price="99,99",
                    amount=5,
                    unit="pcs",
                    total_price="499,95"
                )
            ],
            total_cost="€2.969,07"
        )
        assert extraction.order_lines[0].unit_price == Decimal("1234.56")
        assert extraction.order_lines[0].total_price == Decimal("2469.12")
        assert extraction.order_lines[1].unit_price == Decimal("99.99")
        assert extraction.order_lines[1].total_price == Decimal("499.95")
        assert extraction.total_cost == Decimal("2969.07")
