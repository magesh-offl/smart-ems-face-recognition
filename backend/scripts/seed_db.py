#!/usr/bin/env python3
"""
Database Seeding CLI Script.

This script provides command-line interface for database seeding operations.
Following industry standards, this is a standalone management command that
can be run separately from the main application.

Usage:
    python -m scripts.seed_db           # Seed all data
    python -m scripts.seed_db --status  # Show seeding status
    python -m scripts.seed_db --courses # Seed only courses
    python -m scripts.seed_db --help    # Show help

Architecture:
    CLI Script (this) -> SeederService -> CourseSeeder -> CourseRepository -> MongoDB
    
    Following MVC + Layered + DI:
    - Fixtures: Static data (app/core/fixtures.py)
    - Service: Business logic (app/core/seed.py)  
    - Repository: Data access (app/repositories/course.py)
    - CLI: User interface (this script)
"""
import asyncio
import argparse
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_logging():
    """Configure logging for CLI script."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


async def seed_all(logger):
    """Run all seeders."""
    from app.core.seed import get_seeder_service
    
    logger.info("Starting database seeding...")
    seeder = get_seeder_service()
    results = await seeder.seed_all()
    
    print("\n" + "=" * 50)
    print("SEEDING RESULTS")
    print("=" * 50)
    
    for name, count in results.items():
        if count >= 0:
            print(f"  {name.capitalize()}: {count} created")
        else:
            print(f"  {name.capitalize()}: ERROR")
    
    print("=" * 50 + "\n")
    
    return all(count >= 0 for count in results.values())


async def seed_courses(logger):
    """Seed only courses."""
    from app.core.seed import get_seeder_service
    
    logger.info("Seeding courses...")
    seeder = get_seeder_service()
    count = await seeder.seed_courses()
    
    print(f"\n✓ Seeded {count} courses\n")
    return True


async def show_status(logger):
    """Show current seeding status."""
    from app.core.seed import get_seeder_service
    
    logger.info("Checking seeding status...")
    seeder = get_seeder_service()
    status = await seeder.status()
    
    print("\n" + "=" * 50)
    print("SEEDING STATUS")
    print("=" * 50)
    
    for name, info in status.items():
        print(f"\n{name.upper()}:")
        print(f"  Total fixtures: {info['total']}")
        print(f"  Already seeded: {info['existing']}")
        print(f"  Pending:        {info['pending']}")
    
    print("\n" + "=" * 50 + "\n")
    return True


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Smart EMS Database Seeding Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.seed_db           # Seed all data
  python -m scripts.seed_db --status  # Show seeding status
  python -m scripts.seed_db --courses # Seed only courses
        """
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current seeding status without making changes'
    )
    
    parser.add_argument(
        '--courses',
        action='store_true',
        help='Seed only courses'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='Seed all data (default)'
    )
    
    args = parser.parse_args()
    logger = setup_logging()
    
    try:
        if args.status:
            success = asyncio.run(show_status(logger))
        elif args.courses:
            success = asyncio.run(seed_courses(logger))
        else:
            success = asyncio.run(seed_all(logger))
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
