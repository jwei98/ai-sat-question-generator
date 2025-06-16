#!/usr/bin/env python3
import click
import json
from dotenv import load_dotenv

from models.question import Question
from generators.question_generator import QuestionGenerator
from evaluators.accuracy import AccuracyEvaluator
from utils.display import (
    display_section_header,
    display_question,
    display_evaluation,
    display_summary,
    create_file_output
)

load_dotenv()


@click.group()
def cli():
    """SAT Math Question Generator CLI"""
    pass


@cli.command()
@click.option('--evaluate', is_flag=True, help='Run accuracy evaluation on generated question(s)')
@click.option('--count', '-n', default=1, help='Number of questions to generate')
@click.option('--output', '-o', type=click.File('w'), help='Output file for results (JSON format)')
@click.option('--quiet', is_flag=True, help='Only show summary, suppress individual question display')
def generate(evaluate, count, output, quiet):
    """Generate SAT math question(s)"""
    
    try:
        # Generate question(s)
        generator = QuestionGenerator()
        
        if not quiet:
            click.echo(f"Generating {count} SAT math questions...")
        
        # Generate questions (batching handled internally)
        questions = generator.generate_questions(count)
        
        # Process and display questions
        evaluator = AccuracyEvaluator() if evaluate else None
        results = []
        accurate_count = 0
        
        if evaluate:
            click.echo("Evaluating questions for accuracy...")
        
        for i, question in enumerate(questions, 1):
            result = {
                "id": question.id,
                "question": question.question,
                "choices": question.choices,
                "answer": question.answer
            }
            
            if not quiet:
                display_question(question, i, count)
            
            # Evaluate if requested
            if evaluate:
                evaluation = evaluator.evaluate(question)
                
                if evaluation['correct']:
                    accurate_count += 1
                
                result["evaluation"] = evaluation
                result["accuracy_verified"] = evaluation['correct']
                
                if not quiet:
                    display_evaluation(evaluation)
            
            results.append(result)
        
        # Display summary when evaluation is enabled
        if evaluate and not quiet:
            display_summary(len(results), accurate_count)
        
        # Save to file if requested
        if output:
            file_output = create_file_output(results, evaluate, accurate_count)
            json.dump(file_output, output, indent=2)
            click.echo(f"\nResults saved to: {output.name}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('question_json', type=click.File('r'))
def evaluate_file(question_json):
    """Evaluate a question from a JSON file"""
    
    try:
        # Load question from file
        data = json.load(question_json)
        question = Question(**data)
        
        # Evaluate
        click.echo("Evaluating question accuracy...")
        evaluator = AccuracyEvaluator()
        result = evaluator.evaluate(question)
        
        # Display results
        display_section_header("Question:")
        click.echo(question.format_for_display())
        click.echo(f"\nCorrect Answer: {question.answer}")
        
        display_evaluation(result)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()



if __name__ == '__main__':
    cli()