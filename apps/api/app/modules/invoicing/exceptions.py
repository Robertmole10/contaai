from __future__ import annotations


class InvoicingError(Exception):
    """Base exception for invoicing module."""


#
# Business Partners
#

class BusinessPartnerAlreadyExists(InvoicingError):
    """Business partner already exists."""


class BusinessPartnerNotFound(InvoicingError):
    """Business partner was not found."""


class InvalidBusinessPartner(InvoicingError):
    """Business partner data is invalid."""


#
# Invoices
#

class InvoiceNotFound(InvoicingError):
    """Invoice was not found."""


class InvalidInvoiceState(InvoicingError):
    """Invoice cannot perform requested operation."""


class DuplicateInvoiceNumber(InvoicingError):
    """Invoice number already exists."""


#
# Invoice Lines
#

class InvoiceLineNotFound(InvoicingError):
    """Invoice line was not found."""


class InvalidInvoiceLine(InvoicingError):
    """Invoice line is invalid."""


#
# Calculations
#

class InvalidVatRate(InvoicingError):
    """VAT rate is invalid."""


class InvalidCurrency(InvoicingError):
    """Currency is invalid."""