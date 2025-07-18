# ----------------------------------------
# Todo CLI X - A simple command-line todo application
# This script provides a command-line interface for managing todo tasks.
# It allows users to add, list, complete, delete, and clear tasks.
# ----------------------------------------

# ----------------------------------------
# 📦 Imports
# ----------------------------------------
import argparse
from . import core
from .utils import print_message, format_task_table, print_task_summary
from . import __version__

# ----------------------------------------
# 📝 Main function to handle CLI commands
# ----------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Todo CLI X – A simple and minimalist command-line todo manager.",
        epilog="Use `todo <command> --help` to get more details about a specific command."
    )
    parser.add_argument(
    "--version", "-v", action="version", version=f"todo-cli-x v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", title="Available commands", metavar="")

    # === add command ===
    add_parser = subparsers.add_parser("add", help="Add a new task", description="Add a new task to your todo list with optional priority, due date, and tags.")
    add_parser.add_argument("text", help="The content of the task to add")
    add_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Set task priority (default: medium)"
    )
    add_parser.add_argument(
        "--due",
        type=str,
        help="Set a due date for the task (format: YYYY-MM-DD) - optional"
    )
    add_parser.add_argument(
        "--tags",
        type=str,
        help="Set tags for the task, comma-separated (e.g., work,urgent) - optional"
    )

    # === list command ===
    list_parser = subparsers.add_parser("list", help="List all tasks", description="List all tasks in your todo list with optional filters and sorting.")
    list_parser.add_argument(
        "--done",
        action="store_true",
        help="Show only completed tasks"
    )
    list_parser.add_argument(
        "--undone",
        action="store_true",
        help="Show only uncompleted tasks"
    )
    list_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        help="Filter tasks by priority"
    )
    list_parser.add_argument(
        "--sort",
        choices=["priority"],
        help="Sort tasks by field (currently only 'priority' is supported)"
    )
    list_parser.add_argument(
        "--tags",
        type=str,
        help="Filter tasks by tags, comma-separated (e.g., work,urgent) - optional"
    )
    list_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed task information like creation date and time"
    )


    # === complete command ===
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("id", type=int, help="ID of the task to complete")

    # === clear command ===
    subparsers.add_parser("clear", help="Delete all tasks")

    # === delete command ===
    delete_parser = subparsers.add_parser("delete", help="Delete one or more tasks by their ID")
    delete_parser.add_argument("ids", type=int, nargs="+", help="ID(s) of the task(s) to delete")

    # === edit command ===
    edit_parser = subparsers.add_parser("edit", help="Edit an existing task", description="Edit a task's text, priority, due date or tags.")
    edit_parser.add_argument("id", type=int, help="ID of the task to edit")
    edit_parser.add_argument("--text", type=str, help="New task text")
    edit_parser.add_argument("--priority", choices=["low", "medium", "high"], help="New task priority")
    edit_parser.add_argument("--due", type=str, help="New due date (format: YYYY-MM-DD)")
    edit_parser.add_argument("--tags", type=str, help="New tags, comma-separated (e.g. work,urgent)")

    args = parser.parse_args()

# ----------------------------------------
# 📝 Command handling
# ----------------------------------------

    # If no command is provided, show the welcome message and available commands
    if not args.command:
        print("""
👋 Welcome to Todo CLI X!

This is a simple and minimalist command-line todo manager.

📦 Available commands:
• todo add "Task content" [--priority low|medium|high] [--due YYYY-MM-DD] [--tags tag1,tag2]      ➜ Add a new task with optional priority (default: medium) and due date
• todo list [--done | --undone] [--priority ...] [--tags work,urgent] [--sort priority]           ➜ List tasks with optional filters and sorting
• todo complete <id>                                                                              ➜ Mark a task as completed by ID
• todo delete <id>                                                                                ➜ Delete a task by ID
• todo edit <id> [--text ...] [--priority low|medium|high] [--due YYYY-MM-DD] [--tags tag1,tag2]  ➜ Edit an existing task
• todo clear                                                                                      ➜ Delete all tasks

ℹ️  Run `todo --help` for more details.
        """)
        return

    # Add command handling
    if args.command == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        task = core.add_task(args.text, priority=args.priority, due=args.due, tags=tags)
        if task:
            meta_parts = [f"priority: {task['priority']}"]
            if task.get("due"):
                meta_parts.append(f"due: {task['due']}")
            if task.get("created"):
                meta_parts.append(f"created: {task['created']}")
            if task.get("tags"):
                tags_str = ", ".join(tags)
                meta_parts.append(f"tags: {tags_str}")

            meta_str = " ".join(f"({part})" for part in meta_parts)

            print_message("success", f'Task added: [{task["id"]}] {task["text"]} {meta_str}')
            print()
            print_message("info", "You can now list your tasks with `todo list`.")

    # List command handling
    elif args.command == "list":
        tasks = core.list_tasks()

        # Check if there are any tasks to display
        if args.done and args.undone:
            print_message("warning", "You can't use --done and --undone together.")
            print()
            print_message("info", "Please choose one of them to filter tasks.")
            return
        
        # Filter tasks based on command-line arguments
        if args.done:
            tasks = [task for task in tasks if task["done"]]
        elif args.undone:
            tasks = [task for task in tasks if not task["done"]]

        # Filter by priority if specified
        if args.priority:
            tasks = [t for t in tasks if t["priority"] == args.priority]

        # Sort tasks if specified
        if args.sort == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            tasks.sort(key=lambda t: priority_order.get(t["priority"], 1))

        # Filter by tags if specified
        if args.tags:
            requested_tags = {tag.strip().lower() for tag in args.tags.split(",")}
            filtered_tasks: list[core.Task] = []
            for t in tasks:
                tags = t.get("tags") or []
                task_tags = {tag.lower() for tag in tags}
                if requested_tags & task_tags:
                    filtered_tasks.append(t)
            tasks = filtered_tasks

        # If no tasks match the filters, show a message
        if not tasks:
            print_message("info", "No tasks found.")
        else:
            print(format_task_table(tasks, verbose=args.verbose))
            print_task_summary(tasks)

    # Complete command handling
    elif args.command == "complete":
        task = core.complete_task(args.id)
        if task:
            print_message("success", f'Task [{task["id"]}] "{task["text"]}" marked as done!')
        else:
            print_message("error", f"Sorry, task [{args.id}] not found.")

    # Clear command handling
    elif args.command == "clear":
        core.clear_tasks()
        print_message("info", "All tasks cleared.")

    # Delete command handling
    elif args.command == "delete":
        for task_id in args.ids:
            task = core.delete_task(task_id)
            if task:
                print_message("delete", f'Task [{task["id"]}] "{task["text"]}" deleted.')
            else:
                print_message("error", f"Sorry, task [{task_id}] not found.")

    # Edit command handling
    elif args.command == "edit":
        # Parse tags cleanly if provided
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

        try:
            updated = core.edit_task(
                task_id=args.id,
                text=args.text,
                priority=args.priority,
                due=args.due,
                tags=tags
            )
        except ValueError as e:
            print_message("error", str(e))
            return

        if updated:
            print_message("success", f'Task [{updated["id"]}] updated: "{updated["text"]}"')
        else:
            print_message("error", f"Task [{args.id}] not found.")

    # If command is not recognized
    else:
        print_message("error", "Unknown command. Use `todo --help` to see available commands.")