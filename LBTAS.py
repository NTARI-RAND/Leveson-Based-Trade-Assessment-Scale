"""
Leveson-Based Trade Assessment Scale (LBTAS)
============================================

A rating logic engine for community platforms where trust must be designed
rather than optimized for engagement. LBTAS adapts Nancy Leveson's
safety-critical software assessment methodology to digital commerce and
community exchange, providing a 6-point bidirectional rating scale with
validation and aggregation logic.

The 6-point scale (-1 to +4):
    +4  Delight                  Anticipates evolution of user practices
                                 and concerns post-transaction
    +3  No Negative Consequences Designed to prevent loss, exceeds basic
                                 quality standards
    +2  Basic Satisfaction       Meets socially acceptable standards
                                 exceeding articulated demands
    +1  Basic Promise            Meets all articulated user demands, no more
     0  Cynical Satisfaction     Fulfills basic promise with little discipline
                                 toward user satisfaction
    -1  No Trust                 User was harmed, exploited, or received
                                 product/service with evidence of no
                                 discipline or malicious intent

The core module provides rating logic only. Persistence, user interfaces,
authentication, and analytics are the responsibility of the integrating
platform. See README.md for integration patterns.

Repository:  https://github.com/NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale
Whitepaper:  https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale

Maintained by:
    Network Theory Applied Research Institute, Inc. (NTARI)
    Forge Laboratory
    1 Dupont Way, Suite 4
    Louisville, KY 40207
    https://ntari.org
    tech@ntari.org

Attribution:
    LBTAS adapts methodology developed by Nancy G. Leveson, Professor of
    Aeronautics and Astronautics at the Massachusetts Institute of Technology.
    Professor Leveson does not endorse the application of her safety-critical
    methodology to commerce assessment and has not restricted NTARI's use of
    the underlying framework. LBTAS is an independent application of methods
    she developed for other purposes; any errors in the adaptation are
    NTARI's alone.

Copyright (C) 2024-2025  Network Theory Applied Research Institute, Inc.

License:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Prior versions of this file indicated MIT licensing; this was inconsistent
    with NTARI's published Licensing and Enforcement Strategy (P2-004), which
    defaults all NTARI software to AGPL-3.0. The authoritative license is and
    has been AGPL-3.0; the MIT designation was a documentation error.
"""


# Rating scale definitions. The keys are the valid integer ratings;
# the values are the canonical descriptions used in user-facing interfaces.
RATING_DESCRIPTIONS = {
    -1: "No Trust - User was harmed, exploited, or received a product or service with evidence of no discipline or malicious intent.",
    0:  "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
    1:  "Basic Promise - Interaction meets all articulated user demands, no more.",
    2:  "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
    3:  "No Negative Consequences - Interaction designed to prevent loss, exceeds basic quality standards.",
    4:  "Delight - Interaction anticipates evolution of user practices and concerns post-transaction.",
}

# Default assessment criteria. Integrating platforms may extend or replace
# these via the criteria argument to add_exchange().
DEFAULT_CRITERIA = ("reliability", "usability", "performance", "support")

# Valid rating range (inclusive on both ends).
MIN_RATING = -1
MAX_RATING = 4


class LevesonRatingSystem:
    """Core LBTAS rating engine.

    Manages a collection of ratable exchanges and provides validation,
    storage, and aggregation of ratings against a multi-criteria framework.

    This class is deliberately stateless beyond its in-memory exchange
    dictionary. Integrating platforms are expected to handle persistence,
    authorization, and user interface concerns externally.
    """

    def __init__(self):
        """Initialize an empty rating system."""
        self.exchanges = {}

    def add_exchange(self, name, criteria=None):
        """Register a new ratable exchange.

        An exchange is any entity that can be rated: a vendor, a customer,
        a transaction, a post, a contribution. The core module treats all
        exchanges generically.

        Args:
            name: A unique string identifier for the exchange.
            criteria: Optional iterable of criterion names. Defaults to
                the four standard criteria (reliability, usability,
                performance, support).

        Raises:
            ValueError: If an exchange with the given name already exists.
        """
        if name in self.exchanges:
            raise ValueError("Exchange '{}' already exists.".format(name))

        if criteria is None:
            criteria = DEFAULT_CRITERIA

        self.exchanges[name] = {criterion: [] for criterion in criteria}

    def submit_rating(self, name, criterion, rating):
        """Record a rating for a specific criterion on a specific exchange.

        This is the primary integration entry point. Platforms should call
        this method after performing their own authorization checks.

        Args:
            name: The identifier of the exchange being rated.
            criterion: The criterion name (e.g., "reliability").
            rating: An integer between -1 and +4 inclusive.

        Raises:
            ValueError: If the exchange does not exist, the criterion is
                not registered for the exchange, or the rating is outside
                the valid range.
        """
        if name not in self.exchanges:
            raise ValueError("Exchange '{}' does not exist.".format(name))

        if criterion not in self.exchanges[name]:
            raise ValueError(
                "Criterion '{}' is not registered for exchange '{}'.".format(
                    criterion, name
                )
            )

        if not isinstance(rating, int) or rating < MIN_RATING or rating > MAX_RATING:
            raise ValueError(
                "Rating must be an integer between {} and {} inclusive; got {}.".format(
                    MIN_RATING, MAX_RATING, rating
                )
            )

        self.exchanges[name][criterion].append(rating)

    def get_rating(self, criterion):
        """Interactive rating collection (demo / CLI use only).

        Prompts the user via stdin for a rating value and validates it.
        Not intended for production integration; use submit_rating() in
        platform contexts.

        Args:
            criterion: The criterion name being rated, shown in the prompt.

        Returns:
            A valid integer rating between -1 and +4.
        """
        while True:
            print("\nRating criterion: {}".format(criterion))
            for value, description in sorted(RATING_DESCRIPTIONS.items()):
                print("  {:>2}: {}".format(value, description))

            try:
                rating = int(input("Enter a rating ({} to {}): ".format(MIN_RATING, MAX_RATING)))
            except ValueError:
                print("Please enter an integer.")
                continue

            if MIN_RATING <= rating <= MAX_RATING:
                return rating

            print("Please enter a number between {} and {}.".format(MIN_RATING, MAX_RATING))

    def rate_exchange(self, name):
        """Interactively rate an exchange across all its criteria.

        Demo / CLI use only. Calls get_rating() for each criterion
        registered to the exchange and stores the result.

        Args:
            name: The identifier of the exchange to rate.

        Raises:
            ValueError: If the exchange does not exist.
        """
        if name not in self.exchanges:
            raise ValueError("Exchange '{}' does not exist.".format(name))

        print("\nRating '{}' on the Leveson-Based Trade Assessment Scale".format(name))
        for criterion in self.exchanges[name]:
            rating = self.get_rating(criterion)
            self.exchanges[name][criterion].append(rating)

    def view_ratings(self, name):
        """Return average ratings for each criterion on a given exchange.

        Args:
            name: The identifier of the exchange.

        Returns:
            A dictionary mapping criterion names to their average rating.
            Criteria with no ratings recorded are omitted from the result.

        Raises:
            ValueError: If the exchange does not exist.
        """
        if name not in self.exchanges:
            raise ValueError("Exchange '{}' does not exist.".format(name))

        summary = {}
        for criterion, ratings in self.exchanges[name].items():
            if ratings:
                summary[criterion] = sum(ratings) / len(ratings)

        return summary

    def get_raw_ratings(self, name):
        """Return the full list of recorded ratings for each criterion.

        Useful for platforms that need to compute their own statistics
        (medians, distributions, weighted averages) beyond simple means.

        Args:
            name: The identifier of the exchange.

        Returns:
            A dictionary mapping criterion names to lists of integer ratings.

        Raises:
            ValueError: If the exchange does not exist.
        """
        if name not in self.exchanges:
            raise ValueError("Exchange '{}' does not exist.".format(name))

        return {
            criterion: list(ratings)
            for criterion, ratings in self.exchanges[name].items()
        }


if __name__ == "__main__":
    # Minimal interactive demo. Not for production use.
    print("LBTAS Interactive Demo")
    print("=" * 40)

    system = LevesonRatingSystem()
    exchange_name = input("Enter an exchange name to rate: ").strip()

    if not exchange_name:
        print("No exchange name provided. Exiting.")
    else:
        system.add_exchange(exchange_name)
        system.rate_exchange(exchange_name)

        print("\nResults for '{}':".format(exchange_name))
        averages = system.view_ratings(exchange_name)
        for criterion, average in averages.items():
            print("  {:<15} {:.2f}".format(criterion, average))
