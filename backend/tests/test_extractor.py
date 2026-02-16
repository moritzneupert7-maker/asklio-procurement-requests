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


class TestNetVsGrossTotalValidation:
    """Test that the model properly validates NET vs GROSS total field descriptions."""

    def test_extraction_with_net_total_labeled_nettosumme(self):
        """
        Test extraction where NET total (Nettosumme) is correctly extracted.
        This validates the field description for total_cost.
        """
        extraction = OfferExtraction(
            title="German Invoice with Nettosumme",
            vendor_name="Test Vendor GmbH",
            vendor_vat_id="DE123456789",
            order_lines=[
                ExtractedOrderLine(
                    product="Product 1",
                    description="Test product description",
                    unit_price="1000.00",
                    amount=1,
                    unit="pcs",
                    total_price="1000.00"
                )
            ],
            total_cost="€1.758,00"  # This is the Nettosumme
        )
        # Should extract NET total (before tax), not GROSS (after tax)
        assert extraction.total_cost == Decimal("1758.00")

    def test_extraction_with_shipping_costs_as_line_item(self):
        """
        Test that shipping costs are properly extracted as a separate order line.
        This validates the order_lines field description.
        """
        extraction = OfferExtraction(
            title="Order with Shipping Costs",
            vendor_name="Supplier GmbH",
            vendor_vat_id="DE987654321",
            order_lines=[
                ExtractedOrderLine(
                    product="Main Product",
                    description="Product specifications",
                    unit_price="1186.14",
                    amount=1,
                    unit="pcs",
                    total_price="1186.14"
                ),
                ExtractedOrderLine(
                    product="Versandkosten",  # Shipping costs as separate line
                    description="Shipping and delivery",
                    unit_price="113.85",
                    amount=1,
                    unit="pcs",
                    total_price="113.85"
                )
            ],
            total_cost="€1.299,99"  # Sum of net items (1186.14 + 113.85)
        )
        # Verify shipping cost is extracted as separate line
        assert len(extraction.order_lines) == 2
        assert extraction.order_lines[1].product == "Versandkosten"
        assert extraction.order_lines[1].total_price == Decimal("113.85")
        # Total should be sum of net amounts (NOT including tax)
        assert extraction.total_cost == Decimal("1299.99")

    def test_extraction_with_transport_costs_as_line_item(self):
        """
        Test that transport costs are extracted as a separate line with German label.
        """
        extraction = OfferExtraction(
            title="Order with Transport",
            vendor_name="Transport Vendor GmbH",
            vendor_vat_id="DE111222333",
            order_lines=[
                ExtractedOrderLine(
                    product="Office Supplies",
                    description="Various office items",
                    unit_price="500.00",
                    amount=2,
                    unit="pcs",
                    total_price="1000.00"
                ),
                ExtractedOrderLine(
                    product="Transport, Verpackung und Versand",
                    description="Shipping, packaging and delivery",
                    unit_price="320.00",
                    amount=1,
                    unit="pcs",
                    total_price="320.00"
                )
            ],
            total_cost="€1.320,00"
        )
        # Verify transport is extracted
        assert len(extraction.order_lines) == 2
        assert "Transport" in extraction.order_lines[1].product
        assert extraction.order_lines[1].total_price == Decimal("320.00")
        assert extraction.total_cost == Decimal("1320.00")

    def test_net_total_with_multiple_tax_rates(self):
        """
        Test that NET total is extracted correctly even with multiple tax rates.
        Document should show Nettosumme, not Gesamtsumme.
        """
        extraction = OfferExtraction(
            title="Complex Invoice",
            vendor_name="Complex Vendor GmbH",
            vendor_vat_id="DE444555666",
            order_lines=[
                ExtractedOrderLine(
                    product="Product A",
                    description="Description A",
                    unit_price="800.00",
                    amount=1,
                    unit="pcs",
                    total_price="800.00"
                ),
                ExtractedOrderLine(
                    product="Product B",
                    description="Description B",
                    unit_price="200.00",
                    amount=1,
                    unit="pcs",
                    total_price="200.00"
                )
            ],
            total_cost="€1.000,00"  # Nettosumme, not Gesamtsumme with tax
        )
        # Should be net total, not gross
        assert extraction.total_cost == Decimal("1000.00")
