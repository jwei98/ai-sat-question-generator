#!/usr/bin/env python3
import click
import json
from dotenv import load_dotenv

from models.question import Question
from generators.question_generator import QuestionGenerator
from evaluators.accuracy import AccuracyEvaluator

load_dotenv()


@click.group()
def cli():
    """SAT Math Question Generator CLI"""
    pass


@cli.command()
@click.option('--evaluate', is_flag=True, help='Run accuracy evaluation on generated question')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
def generate(evaluate, output_json):
    """Generate a new SAT math question"""
    
    try:
        # Generate question
        generator = QuestionGenerator()
        click.echo("Generating SAT math question...")
        question = generator.generate_question()
        
        # Display question
        if output_json:
            output = {
                "id": question.id,
                "content": question.content,
                "choices": question.choices,
                "correct_answer": question.correct_answer
            }
        else:
            click.echo("\n" + "="*50)
            click.echo("Generated Question:")
            click.echo("="*50)
            click.echo(question.format_for_display())
            click.echo(f"\nCorrect Answer: {question.correct_answer}")
            click.echo("="*50)
        
        # Evaluate if requested
        if evaluate:
            click.echo("\nEvaluating accuracy...")
            evaluator = AccuracyEvaluator()
            result = evaluator.evaluate(question)
            
            if output_json:
                output["evaluation"] = result
            else:
                click.echo("\n" + "-"*50)
                click.echo("Accuracy Evaluation:")
                click.echo("-"*50)
                click.echo(f"Mathematically Correct: {'' if result['correct'] else ''}")
                click.echo(f"Explanation: {result['explanation']}")
                if result.get('solution_steps'):
                    click.echo(f"\nSolution Steps:\n{result['solution_steps']}")
                click.echo("-"*50)
        
        if output_json:
            click.echo(json.dumps(output, indent=2))
            
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
        click.echo("\n" + "="*50)
        click.echo("Question:")
        click.echo("="*50)
        click.echo(question.format_for_display())
        click.echo(f"\nCorrect Answer: {question.correct_answer}")
        
        click.echo("\n" + "-"*50)
        click.echo("Accuracy Evaluation:")
        click.echo("-"*50)
        click.echo(f"Mathematically Correct: {'' if result['correct'] else ''}")
        click.echo(f"Explanation: {result['explanation']}")
        if result.get('solution_steps'):
            click.echo(f"\nSolution Steps:\n{result['solution_steps']}")
        click.echo("-"*50)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--count', '-n', default=5, help='Number of questions to generate')
@click.option('--output', '-o', type=click.File('w'), help='Output file for batch results')
def batch(count, output):
    """Generate multiple questions in batch"""
    
    generator = QuestionGenerator()
    evaluator = AccuracyEvaluator()
    
    results = []
    accurate_count = 0
    
    click.echo(f"Generating {count} SAT math questions...\n")
    
    with click.progressbar(range(count), label='Generating questions') as bar:
        for i in bar:
            try:
                # Generate question
                question = generator.generate_question()
                
                # Evaluate accuracy
                evaluation = evaluator.evaluate(question)
                
                if evaluation['correct']:
                    accurate_count += 1
                
                # Store result
                result = {
                    "id": question.id,
                    "content": question.content,
                    "choices": question.choices,
                    "correct_answer": question.correct_answer,
                    "accuracy_verified": evaluation['correct']
                }
                results.append(result)
                
            except Exception as e:
                click.echo(f"\nError generating question {i+1}: {e}", err=True)
    
    # Display summary
    click.echo(f"\n\nGeneration Complete!")
    click.echo(f"Total Questions: {count}")
    click.echo(f"Mathematically Accurate: {accurate_count} ({accurate_count/count*100:.1f}%)")
    
    # Save to file if requested
    if output:
        json.dump({
            "questions": results,
            "summary": {
                "total": count,
                "accurate": accurate_count,
                "accuracy_rate": accurate_count/count
            }
        }, output, indent=2)
        click.echo(f"\nResults saved to: {output.name}")
    

if __name__ == '__main__':
    cli()