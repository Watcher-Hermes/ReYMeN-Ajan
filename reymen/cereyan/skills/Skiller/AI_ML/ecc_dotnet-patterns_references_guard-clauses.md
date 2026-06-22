## Guard Clauses

```csharp
// Good: Early returns with clear validation
public async Task<ProcessResult> ProcessPaymentAsync(
    PaymentRequest request,
    CancellationToken cancellationToken)
{
    ArgumentNullException.ThrowIfNull(request);

    if (request.Amount <= 0)
        throw new ArgumentOutOfRangeException(nameof(request.Amount), "Amount must be positive");

    if (string.IsNullOrWhiteSpace(request.Currency))
        throw new ArgumentException("Currency is required", nameof(request.Currency));

    // Happy path continues here without nesting
    var gateway = _gatewayFactory.Create(request.Currency);
    return await gateway.ChargeAsync(request, cancellationToken);
}
```