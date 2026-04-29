import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Book:
    id: int
    title: str
    author: str
    category: str
    available: bool = True


@dataclass
class BorrowRecord:
    user_id: int
    book_id: int
    borrowed_at: datetime
    due_date: datetime
    returned: bool = False
    fine: float = 0.0


class LibraryAPI:
    def __init__(self) -> None:
        self.books: List[Book] = [
            Book(1, "Python Basics", "John Smith", "Programming"),
            Book(2, "Database Design", "Alice Brown", "Technology"),
            Book(3, "Web Development", "Mark Jones", "Programming"),
            Book(4, "Introduction to AI", "Sarah White", "Technology"),
            Book(5, "English Grammar", "Peter Johnson", "Education"),
        ]
        self.records: List[BorrowRecord] = []
        self.lock = asyncio.Lock()

    async def get_books(self) -> List[Book]:
        await asyncio.sleep(1)
        return self.books

    async def search_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Book]:
        await asyncio.sleep(1)

        results = self.books

        if title:
            results = [book for book in results if title.lower() in book.title.lower()]
        if author:
            results = [book for book in results if author.lower() in book.author.lower()]
        if category:
            results = [book for book in results if category.lower() in book.category.lower()]

        return results

    async def borrow_book(self, user_id: int, book_id: int) -> str:
        async with self.lock:
            await asyncio.sleep(4)

            book = next((b for b in self.books if b.id == book_id), None)

            if book is None:
                return f"User {user_id}: Book not found."

            if not book.available:
                return f"User {user_id}: '{book.title}' is already borrowed."

            book.available = False
            borrowed_at = datetime.now()
            due_date = borrowed_at + timedelta(days=7)

            record = BorrowRecord(
                user_id=user_id,
                book_id=book_id,
                borrowed_at=borrowed_at,
                due_date=due_date
            )
            self.records.append(record)

            return (
                f"User {user_id}: Successfully borrowed '{book.title}'. "
                f"Due date: {due_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    async def return_book(self, user_id: int, book_id: int) -> str:
        async with self.lock:
            await asyncio.sleep(4)

            record = next(
                (
                    r for r in self.records
                    if r.user_id == user_id and r.book_id == book_id and not r.returned
                ),
                None
            )

            if record is None:
                return f"User {user_id}: No active borrow record found for book ID {book_id}."

            book = next((b for b in self.books if b.id == book_id), None)
            if book is None:
                return f"User {user_id}: Book not found."

            now = datetime.now()
            fine = 0.0

            if now > record.due_date:
                overdue_days = (now - record.due_date).days
                fine = max(0, overdue_days * 5.0)

            record.returned = True
            record.fine = fine
            book.available = True

            return (
                f"User {user_id}: Returned '{book.title}' successfully. "
                f"Fine: Le {fine:.2f}"
            )

    async def check_fines(self, user_id: int) -> float:
        await asyncio.sleep(1)
        total_fine = sum(record.fine for record in self.records if record.user_id == user_id)
        return total_fine


async def show_books(api: LibraryAPI) -> None:
    books = await api.get_books()
    print("\n--- ALL BOOKS ---")
    for book in books:
        status = "Available" if book.available else "Borrowed"
        print(
            f"ID: {book.id}, Title: {book.title}, Author: {book.author}, "
            f"Category: {book.category}, Status: {status}"
        )


async def search_menu(api: LibraryAPI) -> None:
    title = input("Enter title to search (or leave blank): ").strip()
    author = input("Enter author to search (or leave blank): ").strip()
    category = input("Enter category to search (or leave blank): ").strip()

    results = await api.search_books(
        title=title if title else None,
        author=author if author else None,
        category=category if category else None
    )

    print("\n--- SEARCH RESULTS ---")
    if not results:
        print("No books found.")
        return

    for book in results:
        status = "Available" if book.available else "Borrowed"
        print(
            f"ID: {book.id}, Title: {book.title}, Author: {book.author}, "
            f"Category: {book.category}, Status: {status}"
        )


async def borrow_menu(api: LibraryAPI) -> None:
    try:
        user_id = int(input("Enter user ID: "))
        book_id = int(input("Enter book ID to borrow: "))
        result = await api.borrow_book(user_id, book_id)
        print(result)
    except ValueError:
        print("Invalid input. Please enter numbers only.")


async def return_menu(api: LibraryAPI) -> None:
    try:
        user_id = int(input("Enter user ID: "))
        book_id = int(input("Enter book ID to return: "))
        result = await api.return_book(user_id, book_id)
        print(result)
    except ValueError:
        print("Invalid input. Please enter numbers only.")


async def fines_menu(api: LibraryAPI) -> None:
    try:
        user_id = int(input("Enter user ID: "))
        total_fine = await api.check_fines(user_id)
        print(f"User {user_id} total fine: Le {total_fine:.2f}")
    except ValueError:
        print("Invalid input. Please enter numbers only.")


async def simulate_multiple_users(api: LibraryAPI) -> None:
    print("\n--- SIMULATING MULTIPLE USERS BORROWING AT THE SAME TIME ---")

    tasks = [
        api.borrow_book(101, 1),
        api.borrow_book(102, 2),
        api.borrow_book(103, 1),
    ]

    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)


async def main() -> None:
    api = LibraryAPI()

    while True:
        print("\n===== LIBRARY SYSTEM MENU =====")
        print("1. View all books")
        print("2. Search books")
        print("3. Borrow book")
        print("4. Return book")
        print("5. Check fines")
        print("6. Simulate multiple users")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            await show_books(api)
        elif choice == "2":
            await search_menu(api)
        elif choice == "3":
            await borrow_menu(api)
        elif choice == "4":
            await return_menu(api)
        elif choice == "5":
            await fines_menu(api)
        elif choice == "6":
            await simulate_multiple_users(api)
        elif choice == "0":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())