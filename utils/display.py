import click
from models.question import Question


def display_section_header(title: str, separator: str = "=", width: int = 50):
    """Display a section header with separators"""
    click.echo(f"\n{separator * width}")
    click.echo(title)
    click.echo(separator * width)


def display_question(question: Question, index: int = None, total: int = None):
    """Display a question with optional numbering"""
    if index and total:
        display_section_header(f"Question {index}/{total}:")
    else:
        display_section_header("Generated Question:")
    
    click.echo(question.format_for_display())
    click.echo(f"\nCorrect Answer: {question.answer}")
    click.echo("=" * 50)


def display_evaluation(evaluation: dict):
    """Display evaluation results"""
    click.echo("\n" + "-" * 50)
    click.echo("Accuracy Evaluation:")
    click.echo("-" * 50)
    click.echo(f"Mathematically Correct: {'✓' if evaluation['correct'] else '✗'}")
    click.echo(f"Explanation: {evaluation['explanation']}")
    if evaluation.get('solution_steps'):
        click.echo(f"\nSolution Steps:\n{evaluation['solution_steps']}")
    click.echo("-" * 50)


def display_summary(total: int, correct: int):
    """Display summary statistics"""
    display_section_header("SUMMARY")
    click.echo(f"Total Questions Generated: {total}")
    click.echo(f"Mathematically Correct: {correct} ({correct/total*100:.1f}%)")
    click.echo("=" * 50)


def create_file_output(results: list, evaluate: bool, accurate_count: int):
    """Create JSON structure for file output"""
    return {
        "questions": results,
        "summary": {
            "total": len(results),
            "accurate": accurate_count if evaluate else None,
            "accuracy_rate": accurate_count/len(results) if evaluate and results else None
        }
    }