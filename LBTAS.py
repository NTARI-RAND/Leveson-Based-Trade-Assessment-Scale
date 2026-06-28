#!/usr/bin/env python3
"""
Leveson-Based Trade Assessment Scale (LBTAS)
============================================

A rigorous assessment methodology for digital commerce adapted from 
Nancy Leveson's Software Assessment Scale used in aircraft software development.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

__version__ = "2.0.0"
__author__ = "Network Theory Applied Research Institute"
__license__ = "AGPL-3.0"

class LevesonRatingSystem:
    """
    Leveson-Based Trade Assessment Scale rating system.
    
    Provides a rigorous 6-point scale (-1 to +4) for evaluating
    digital commerce interactions based on Nancy Leveson's methodology.
    """
    
    DEFAULT_CATEGORIES = ['reliability', 'usability', 'performance', 'support']
    
    RATING_DESCRIPTIONS = {
        -1: "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.",
        0: "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
        1: "Basic Promise - Interaction meets all articulated user demands, no more.",
        2: "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
        3: "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.",
        4: "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction."
    }

    # Display order for distributions: best (+4) down to worst (-1).
    RATING_LEVELS = [4, 3, 2, 1, 0, -1]

    # Short labels for each level (the part before " - " in RATING_DESCRIPTIONS).
    RATING_LABELS = {
        4: "Delight",
        3: "No Negative Consequences",
        2: "Basic Satisfaction",
        1: "Basic Promise",
        0: "Cynical Satisfaction",
        -1: "No Trust",
    }

    @staticmethod
    def _distribution(ratings: List[int]) -> Dict[str, int]:
        """Count ratings at each level. Keys are level strings -1..+4.

        Ratings are never averaged; the distribution (count per level) is the
        unit of reputation. See CLAUDE.md.
        """
        dist = {str(level): 0 for level in (-1, 0, 1, 2, 3, 4)}
        for rating in ratings:
            dist[str(rating)] += 1
        return dist

    @classmethod
    def _format_distribution(cls, dist: Dict[str, int], indent: str = "  ") -> str:
        """Render a distribution best-to-worst, one line per level: level label : count."""
        lines = []
        for level in cls.RATING_LEVELS:
            sign = f"+{level}" if level > 0 else (" 0" if level == 0 else f"{level}")
            label = cls.RATING_LABELS[level]
            lines.append(f"{indent}{sign} {label:<24}: {dist[str(level)]}")
        return "\n".join(lines)

    def __init__(self, storage_file: Optional[str] = None, categories: Optional[List[str]] = None):
        """
        Initialize the LBTAS rating system.
        
        Args:
            storage_file: Optional path to JSON file for persistent storage
            categories: Custom rating categories (defaults to reliability, usability, performance, support)
        """
        self.categories = categories or self.DEFAULT_CATEGORIES.copy()
        self.storage_file = storage_file
        self.exchanges = {}
        
        if self.storage_file:
            self.load_from_file()
    
    def add_exchange(self, name: str) -> None:
        """Add a new exchange to the system."""
        if name in self.exchanges:
            raise ValueError(f"Exchange '{name}' already exists.")
        
        self.exchanges[name] = {
            category: [] for category in self.categories
        }
        self.exchanges[name]['_metadata'] = {
            'created': datetime.now().isoformat(),
            'total_ratings': 0
        }
        
        if self.storage_file:
            self.save_to_file()
    
    def add_rating(self, exchange_name: str, criterion: str, rating: int) -> None:
        """
        Add a rating programmatically (non-interactive).
        
        Args:
            exchange_name: Name of the exchange
            criterion: Rating category
            rating: Rating value (-1 to 4)
        """
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange '{exchange_name}' does not exist.")
        
        if criterion not in self.categories:
            raise ValueError(f"Criterion '{criterion}' not in valid categories: {self.categories}")
        
        if not isinstance(rating, int) or rating < -1 or rating > 4:
            raise ValueError(f"Rating must be integer between -1 and 4, got {rating}")
        
        self.exchanges[exchange_name][criterion].append(rating)
        self.exchanges[exchange_name]['_metadata']['total_ratings'] += 1
        
        if self.storage_file:
            self.save_to_file()
    
    def get_rating(self, criterion: str) -> int:
        """Get a rating from the user for a specific criterion (interactive)."""
        print(f"\nRate {criterion.capitalize()}:")
        print("=" * 50)
        
        for rating, description in self.RATING_DESCRIPTIONS.items():
            print(f" {rating:2d}: {description}")
        
        print("=" * 50)
        
        while True:
            try:
                rating = int(input(f"Enter your rating for {criterion.capitalize()} (-1 to 4): "))
                if -1 <= rating <= 4:
                    return rating
                else:
                    print("Please enter a rating between -1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a number between -1 and 4.")
            except KeyboardInterrupt:
                print("\nRating cancelled.")
                sys.exit(0)
    
    def rate_exchange(self, name: str) -> None:
        """Rate an exchange based on Leveson Software Assessment Scale (interactive)."""
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")
        
        print(f"\nRating '{name}' using Leveson-Based Trade Assessment Scale")
        print("=" * 60)
        
        for criterion in self.categories:
            rating = self.get_rating(criterion)
            self.exchanges[name][criterion].append(rating)
            self.exchanges[name]['_metadata']['total_ratings'] += 1
        
        if self.storage_file:
            self.save_to_file()
        
        print(f"\nRating completed for '{name}'!")
    
    def view_ratings(self, name: str) -> Dict[str, Dict]:
        """Return the rating distribution for each criterion on an exchange.

        Ratings are never averaged. Each criterion maps to the count at every
        level (-1..+4) plus the category total::

            {"<category>": {"distribution": {"-1": 0, ..., "4": 0}, "total": 0}}
        """
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")

        summary = {}
        for criterion in self.categories:
            ratings = self.exchanges[name][criterion]
            summary[criterion] = {
                'distribution': self._distribution(ratings),
                'total': len(ratings),
            }
        return summary
    
    def get_all_exchanges(self) -> List[str]:
        """Return a list of all exchanges."""
        return list(self.exchanges.keys())
    
    def generate_report(self) -> Dict:
        """Generate a system report as rating distributions (never averages).

        Reputation is the count at each level plus the total. There is no
        system average, no category means, and no average-ranked performer
        lists. ``harm_flagged`` lists exchanges that received one or more -1
        ("No Trust") ratings, sorted by -1 count descending.
        """
        total_exchanges = len(self.exchanges)

        if total_exchanges == 0:
            return {
                'total_exchanges': 0,
                'total_ratings': 0,
                'overall_distribution': self._distribution([]),
                'category_distributions': {cat: self._distribution([]) for cat in self.categories},
                'exchange_distributions': {},
                'harm_flagged': [],
                'generated_at': datetime.now().isoformat(),
            }

        overall_ratings = []
        category_totals = {cat: [] for cat in self.categories}
        exchange_distributions = {}
        harm_counts = {}

        for exchange_name, exchange_data in self.exchanges.items():
            exchange_ratings = []
            for category in self.categories:
                ratings = exchange_data[category]
                category_totals[category].extend(ratings)
                exchange_ratings.extend(ratings)
                overall_ratings.extend(ratings)

            dist = self._distribution(exchange_ratings)
            exchange_distributions[exchange_name] = {
                'distribution': dist,
                'total': len(exchange_ratings),
            }
            if dist['-1'] > 0:
                harm_counts[exchange_name] = dist['-1']

        # Sort harm-flagged exchanges by -1 count descending, then name for stability.
        harm_flagged = sorted(harm_counts.items(), key=lambda kv: (-kv[1], kv[0]))

        return {
            'total_exchanges': total_exchanges,
            'total_ratings': len(overall_ratings),
            'overall_distribution': self._distribution(overall_ratings),
            'category_distributions': {
                cat: self._distribution(ratings) for cat, ratings in category_totals.items()
            },
            'exchange_distributions': exchange_distributions,
            'harm_flagged': [[name, count] for name, count in harm_flagged],
            'generated_at': datetime.now().isoformat(),
        }
    
    def save_to_file(self) -> None:
        """Save exchanges to JSON file."""
        if not self.storage_file:
            return
        
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.exchanges, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save to {self.storage_file}: {e}")
    
    def load_from_file(self) -> None:
        """Load exchanges from JSON file."""
        if not self.storage_file or not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validate loaded data structure
                for exchange_name, exchange_data in data.items():
                    if not isinstance(exchange_data, dict):
                        continue
                    # Ensure all categories exist
                    for category in self.categories:
                        if category not in exchange_data:
                            exchange_data[category] = []
                    # Ensure metadata exists
                    if '_metadata' not in exchange_data:
                        exchange_data['_metadata'] = {
                            'created': datetime.now().isoformat(),
                            'total_ratings': sum(len(ratings) for cat, ratings in exchange_data.items() if cat != '_metadata')
                        }
                
                self.exchanges = data
        except Exception as e:
            print(f"Warning: Could not load from {self.storage_file}: {e}")
    
    def export_to_csv(self, filename: str) -> None:
        """Export ratings to CSV (columns: exchange, category, rating, index).

        No timestamp column: the CLI store does not record per-rating times, so
        writing ``datetime.now()`` on every row would falsely imply each rating
        was made at export time. Honest per-rating timestamps live only in the
        API event records. ``index`` is the 1-based position of the rating
        within its category, matching the Go/Rust/TypeScript exports.
        """
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['exchange', 'category', 'rating', 'index']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for exchange_name, exchange_data in self.exchanges.items():
                for category in self.categories:
                    for index, rating in enumerate(exchange_data[category], start=1):
                        writer.writerow({
                            'exchange': exchange_name,
                            'category': category,
                            'rating': rating,
                            'index': index,
                        })

def main():
    """Command-line interface for LBTAS."""
    parser = argparse.ArgumentParser(
        description="Leveson-Based Trade Assessment Scale (LBTAS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lbtas rate --exchange "MyService"
  lbtas add --exchange "MyService" --criterion reliability --rating 3
  lbtas view --exchange "MyService"
  lbtas report
  lbtas export --format csv --output ratings.csv
        """
    )
    
    parser.add_argument('--version', action='version', version=f'LBTAS {__version__}')
    parser.add_argument('--storage', default='lbtas_ratings.json', 
                       help='Storage file for ratings (default: lbtas_ratings.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Rate command (interactive)
    rate_parser = subparsers.add_parser('rate', help='Rate an exchange interactively')
    rate_parser.add_argument('--exchange', required=True, help='Exchange name to rate')
    
    # Add command (programmatic)
    add_parser = subparsers.add_parser('add', help='Add a rating programmatically')
    add_parser.add_argument('--exchange', required=True, help='Exchange name')
    add_parser.add_argument('--criterion', required=True, help='Rating criterion')
    add_parser.add_argument('--rating', type=int, required=True, help='Rating value (-1 to 4)')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View ratings for an exchange')
    view_parser.add_argument('--exchange', required=True, help='Exchange name to view')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all exchanges')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate system report')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export ratings')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--output', required=True, help='Output filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize rating system
    rating_system = LevesonRatingSystem(storage_file=args.storage)
    
    try:
        if args.command == 'rate':
            if args.exchange not in rating_system.get_all_exchanges():
                rating_system.add_exchange(args.exchange)
            rating_system.rate_exchange(args.exchange)
            
        elif args.command == 'add':
            if args.exchange not in rating_system.get_all_exchanges():
                rating_system.add_exchange(args.exchange)
            rating_system.add_rating(args.exchange, args.criterion, args.rating)
            print(f"Added rating {args.rating} for {args.criterion} to {args.exchange}")
            
        elif args.command == 'view':
            ratings = rating_system.view_ratings(args.exchange)
            metadata = rating_system.exchanges[args.exchange].get('_metadata', {})
            created = metadata.get('created', 'unknown')
            exchange_total = sum(block['total'] for block in ratings.values())
            print(f"\nRatings for '{args.exchange}':")
            print("=" * 40)
            print(f"In service since: {created}")
            print(f"Total ratings (transaction volume): {exchange_total}")
            for criterion, block in ratings.items():
                print(f"\n{criterion.capitalize()} (total: {block['total']}):")
                print(LevesonRatingSystem._format_distribution(block['distribution']))

        elif args.command == 'list':
            exchanges = rating_system.get_all_exchanges()
            if exchanges:
                print("Registered exchanges:")
                for exchange in exchanges:
                    ratings = rating_system.view_ratings(exchange)
                    total = sum(block['total'] for block in ratings.values())
                    harm = sum(block['distribution']['-1'] for block in ratings.values())
                    line = f"  {exchange} ({total} ratings)"
                    if harm > 0:
                        line += f", {harm}x -1 No Trust"
                    print(line)
            else:
                print("No exchanges registered.")

        elif args.command == 'report':
            report = rating_system.generate_report()
            print("\nLBTAS System Report")
            print("=" * 50)
            print(f"Total exchanges: {report['total_exchanges']}")
            print(f"Total ratings (transaction volume): {report['total_ratings']}")

            print("\nOverall distribution:")
            print(LevesonRatingSystem._format_distribution(report['overall_distribution']))

            print("\nCategory distributions:")
            for category, dist in report['category_distributions'].items():
                print(f"  {category.capitalize()}:")
                print(LevesonRatingSystem._format_distribution(dist, indent="    "))

            if report['exchange_distributions']:
                print("\nPer-exchange distributions:")
                for exchange_name, block in report['exchange_distributions'].items():
                    created = rating_system.exchanges[exchange_name].get('_metadata', {}).get('created', 'unknown')
                    print(f"  {exchange_name} (transaction volume: {block['total']}, in service since: {created}):")
                    print(LevesonRatingSystem._format_distribution(block['distribution'], indent="    "))

            if report['harm_flagged']:
                print("\nHarm-flagged exchanges (received -1 No Trust):")
                for exchange_name, count in report['harm_flagged']:
                    print(f"  {exchange_name}: {count}x -1")
                    
        elif args.command == 'export':
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    json.dump(rating_system.exchanges, f, indent=2)
            elif args.format == 'csv':
                rating_system.export_to_csv(args.output)
            print(f"Exported to {args.output}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Example usage when run as script
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive demo mode
        print("LBTAS Interactive Demo")
        print("=" * 50)
        print("Welcome to the Leveson-Based Trade Assessment Scale!")
        print("This demo will walk you through rating a service.\n")
        
        rating_system = LevesonRatingSystem()
        
        try:
            # Demo exchange
            demo_exchange = "DemoService"
            print(f"Creating demo exchange: '{demo_exchange}'")
            rating_system.add_exchange(demo_exchange)
            
            print("\nYou can now rate this service on four criteria:")
            print("- Reliability: How dependable and consistent is it?")
            print("- Usability: How easy and pleasant is it to use?") 
            print("- Performance: How fast and efficient is it?")
            print("- Support: How helpful is customer service?")
            
            print("\nWould you like to rate this demo service? (y/n): ", end="")
            if input().lower().startswith('y'):
                rating_system.rate_exchange(demo_exchange)
                
                # Show results as a distribution (ratings are never averaged).
                ratings = rating_system.view_ratings(demo_exchange)
                print(f"\nYour ratings for '{demo_exchange}':")
                print("-" * 30)
                for criterion, block in ratings.items():
                    print(f"\n{criterion.capitalize()} (total: {block['total']}):")
                    print(LevesonRatingSystem._format_distribution(block['distribution']))
                print("\nRatings are recorded as a distribution (count per level), never averaged.")
            else:
                print("Demo completed. Try 'python lbtas.py --help' for CLI options.")
                
        except KeyboardInterrupt:
            print("\nDemo cancelled. Goodbye!")
        except Exception as e:
            print(f"Demo error: {e}")
    else:
        # Use CLI interface
        main()
