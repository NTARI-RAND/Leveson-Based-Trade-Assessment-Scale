# Leveson-Based Trade Assessment Scale (LBTAS)

A rating logic engine for community platforms where trust must be designed rather than optimized for engagement.

LBTAS adapts Nancy Leveson's safety-critical software assessment methodology to digital commerce and community exchange. It provides a 6-point bidirectional rating scale with validation and aggregation logic, designed to integrate into platforms that take trust seriously enough to treat their rating systems as safety-critical infrastructure.

Maintained by the [Network Theory Applied Research Institute](https://ntari.org) Forge Laboratory.

## Why This Exists

Conventional rating systems — five stars, thumbs up, net promoter scores — are optimized for ranking and discovery. They tell a platform which items to surface. They do not tell a platform whether the exchanges happening on it are safe, fair, or producing the trust the platform claims to enable.

Nancy Leveson's work on safety-critical software, including the systems used to evaluate aircraft control systems, established that safety is an emergent property of the system as a whole rather than a property of any individual component. Components can work as specified while the system fails. The failure mode is in the control structure, not the parts.

LBTAS applies this insight to commerce and community exchange. Trust is emergent. Rating systems are themselves safety-critical infrastructure. Get the rating logic wrong and you get the failure modes platform capitalism has spent two decades demonstrating: capture, asymmetric power, predatory dynamics that no individual review can flag because the failure is structural.

For the longer argument and research context, see the [LBTAS whitepaper](https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale).

## The Scale

LBTAS uses a 6-point scale from -1 to +4. Each point has a specific definition that ties the rating to observable properties of the exchange, not to subjective satisfaction.

| Rating | Name | Definition |
|--------|------|------------|
| **+4** | Delight | Interaction anticipates evolution of user practices and concerns post-transaction |
| **+3** | No Negative Consequences | Interaction designed to prevent loss, exceeds basic quality standards |
| **+2** | Basic Satisfaction | Interaction meets socially acceptable standards exceeding articulated demands |
| **+1** | Basic Promise | Interaction meets all articulated user demands, no more |
| **0** | Cynical Satisfaction | Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction |
| **-1** | No Trust | User was harmed, exploited, or received a product or service with evidence of no discipline or malicious intent |

The asymmetric range (one negative point, four positive points) is deliberate. A single -1 rating signals a structural failure that warrants investigation; the gradations above zero capture the difference between a platform that meets its obligations and one that builds toward genuine user benefit.

## What LBTAS Provides

The core module is intentionally narrow. It handles:

- **Rating validation** against the -1 to +4 scale
- **Exchange management** for any ratable entity (vendors, customers, transactions, posts, contributions)
- **Multi-criteria assessment** across four standard dimensions: reliability, usability, performance, support
- **Statistical aggregation** including averages and raw rating retrieval
- **Bidirectional assessment** through context-agnostic entity treatment — both parties to an exchange can be rated by using the same underlying logic

The module deliberately does not handle persistence, user interfaces, authentication, authorization, or analytics. Those belong to the integrating platform.

## What Your Platform Must Provide

Integration requires you to handle:

- **Database persistence** for ratings and audit trails
- **User authentication and authorization** including the business logic of who can rate whom and when
- **Rating collection interfaces** presenting the scale with clear definitions to users
- **Aggregation displays** for showing accumulated ratings meaningfully
- **Dispute resolution workflows** for contested ratings

This separation is the point. LBTAS is the rating logic; you bring everything else. The result is that LBTAS works in any platform context — e-commerce, member communities, cooperative networks, mutual aid platforms — without dragging in opinionated decisions about the rest of your stack.

## Installation

```bash
git clone https://github.com/NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
```

Requires Python 3.6 or later. No external dependencies.

## Minimal Integration Example

```python
from LBTAS import LevesonRatingSystem

# Initialize the rating engine
rating_system = LevesonRatingSystem()

# Register an exchange (vendor, customer, transaction, post — anything ratable)
rating_system.add_exchange("vendor_acme_farms")

# Submit ratings against the four criteria
# In production, these values come from your UI after authorization checks
rating_system.submit_rating("vendor_acme_farms", "reliability", 3)
rating_system.submit_rating("vendor_acme_farms", "usability", 2)
rating_system.submit_rating("vendor_acme_farms", "performance", 4)
rating_system.submit_rating("vendor_acme_farms", "support", 3)

# Retrieve aggregated ratings
averages = rating_system.view_ratings("vendor_acme_farms")
# Returns: {'reliability': 3.0, 'usability': 2.0, 'performance': 4.0, 'support': 3.0}
```

For bidirectional assessment, register both parties as separate exchanges:

```python
rating_system.add_exchange("vendor_acme_farms")
rating_system.add_exchange("customer_jdoe")
# Customer rates vendor, vendor rates customer — same logic, no special routing
```

## Integration Pattern

A typical platform integration looks like this:

```python
from LBTAS import LevesonRatingSystem

class PlatformRatingService:
    def __init__(self, database, auth_service):
        self.lbtas = LevesonRatingSystem()
        self.database = database
        self.auth = auth_service

    def submit_rating(self, user_id, exchange_id, criterion, rating):
        # Platform handles authorization
        if not self.auth.can_rate(user_id, exchange_id):
            raise PermissionError("User not authorized to rate this exchange")

        # LBTAS handles validation and aggregation
        if exchange_id not in self.lbtas.exchanges:
            self.lbtas.add_exchange(exchange_id)
        self.lbtas.submit_rating(exchange_id, criterion, rating)

        # Platform handles persistence
        self.database.store_rating(user_id, exchange_id, criterion, rating)

    def get_aggregated_ratings(self, exchange_id):
        # Load historical ratings from database into LBTAS
        if exchange_id not in self.lbtas.exchanges:
            self.lbtas.add_exchange(exchange_id)
        for record in self.database.get_ratings(exchange_id):
            self.lbtas.submit_rating(exchange_id, record.criterion, record.rating)
        return self.lbtas.view_ratings(exchange_id)
```

## Recommended Database Schema

```sql
CREATE TABLE lbtas_ratings (
    id SERIAL PRIMARY KEY,
    exchange_id VARCHAR(255) NOT NULL,
    rater_id VARCHAR(255) NOT NULL,
    criterion VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating >= -1 AND rating <= 4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
);

CREATE INDEX idx_lbtas_exchange ON lbtas_ratings(exchange_id);
CREATE INDEX idx_lbtas_rater ON lbtas_ratings(rater_id);
```

## Extending the Criteria

The four default criteria (reliability, usability, performance, support) are extensible. If your domain requires additional dimensions — for example, ecological impact for an agricultural network, or accessibility for a civic platform — you can subclass `LevesonRatingSystem` or pass a custom criteria list to `add_exchange()`. The rating logic, validation, and aggregation work identically across any criteria set.

We recommend keeping criteria small in number (four to six maximum) and definable in a single sentence each. Users do not reliably distinguish more than a handful of evaluation dimensions in a single rating event.

## License

LBTAS is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See [LICENSE](./LICENSE) for the full text.

This licensing choice is structural. NTARI's [Licensing and Enforcement Strategy (P2-004)](https://www.ntari.org/post/licensing-and-enforcement-strategy-ntari-policy-p2-004) defaults all NTARI software to AGPL-3.0 specifically to prevent re-privatization of community infrastructure. If you integrate LBTAS into a network service, the AGPL requires you to make your modified source available to your users. We consider this a feature, not a constraint — rating infrastructure that can be captured and closed is rating infrastructure that will be.

**Note on prior versions:** Earlier copies of the source file header indicated MIT licensing. This was a documentation error inconsistent with NTARI's published policy. The authoritative license is AGPL-3.0. Use under MIT terms prior to this correction is honored; new derivative work follows AGPL-3.0.

## Attribution

LBTAS adapts methodology developed by Nancy G. Leveson, Professor of Aeronautics and Astronautics at the Massachusetts Institute of Technology. Her work on safety-critical systems — including STAMP (Systems-Theoretic Accident Model and Processes), the analysis of the Therac-25 accidents, and the Traffic Collision Avoidance System — established the systems-theoretic frame that LBTAS extends into commerce and community exchange contexts.

Professor Leveson has been informed of this work and does not endorse the application of her safety-critical methodology to commerce assessment. She has not restricted NTARI's use of the underlying framework. LBTAS is therefore an independent application of methods she developed for other purposes, and any errors in the adaptation are NTARI's alone. Her academic work is published independently of this project and should be consulted directly for authoritative treatment of safety-critical software assessment.

## Contributing

Volunteer contributors are welcome. NTARI recruits in Go, JavaScript, technical writing, and community organizing roles. Reach out at tech@ntari.org to discuss integration or contribution.

For governance questions, licensing inquiries, or coordination with NTARI's other projects (AgriNet, SoHoLINK, Open Civic Standard), contact policy@ntari.org.

## Citation

If you reference LBTAS in academic work, please cite:

> Network Theory Applied Research Institute. (2025). *Leveson-Based Trade Assessment Scale (LBTAS): A Research Framework for Digital Commerce Rating Systems* (Version 3.0). https://github.com/NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale
