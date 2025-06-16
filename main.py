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
@click.option('--evaluate', is_flag=True, help='Run accuracy evaluation on generated question(s)')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
@click.option('--count', '-n', default=1, help='Number of questions to generate')
@click.option('--output', '-o', type=click.File('w'), help='Output file for results')
@click.option('--quiet', is_flag=True, help='Only show summary, suppress individual question display')
def generate(evaluate, output_json, count, output, quiet):
    """Generate SAT math question(s)"""
    
    try:
        # Generate question(s)
        generator = QuestionGenerator()
        
        if not quiet:
            click.echo(f"Generating {count} SAT math questions...")
        
        # Generate questions efficiently in chunks if needed
        if count <= 10:
            questions = generator.generate_questions(count)
        else:
            # For larger batches, generate in chunks of 10
            questions = []
            chunks = (count + 9) // 10  # Round up division
            for chunk_idx in range(chunks):
                remaining = count - len(questions)
                chunk_size = min(10, remaining)
                try:
                    chunk_questions = generator.generate_questions(chunk_size)
                    questions.extend(chunk_questions)
                except Exception as e:
                    click.echo(f"Error generating chunk {chunk_idx+1}: {e}", err=True)
        
        # Process and display questions
        evaluator = AccuracyEvaluator() if evaluate else None
        results = []
        accurate_count = 0
        
        if evaluate and count > 1:
            click.echo("Evaluating questions for accuracy...")
        
        for i, question in enumerate(questions, 1):
            result = {
                "id": question.id,
                "question": question.question,
                "choices": question.choices,
                "answer": question.answer
            }
            
            if not output_json and not quiet:
                if count > 1:
                    click.echo(f"\n{'='*50}")
                    click.echo(f"Question {i}/{count}:")
                    click.echo("="*50)
                else:
                    click.echo("\n" + "="*50)
                    click.echo("Generated Question:")
                    click.echo("="*50)
                click.echo(question.format_for_display())
                click.echo(f"\nCorrect Answer: {question.answer}")
                click.echo("="*50)
            
            # Evaluate if requested
            if evaluate:
                if not output_json and not quiet and count == 1:
                    click.echo("\nEvaluating accuracy...")
                evaluation = evaluator.evaluate(question)
                
                if evaluation['correct']:
                    accurate_count += 1
                
                result["evaluation"] = evaluation
                result["accuracy_verified"] = evaluation['correct']
                
                if not output_json and not quiet:
                    click.echo("\n" + "-"*50)
                    click.echo("Accuracy Evaluation:")
                    click.echo("-"*50)
                    click.echo(f"Mathematically Correct: {'✓' if evaluation['correct'] else '✗'}")
                    click.echo(f"Explanation: {evaluation['explanation']}")
                    if evaluation.get('solution_steps'):
                        click.echo(f"\nSolution Steps:\n{evaluation['solution_steps']}")
                    click.echo("-"*50)
            
            results.append(result)
        
        # Display summary for multiple questions with evaluation
        if evaluate and count > 1 and not output_json:
            click.echo(f"\n\n{'='*50}")
            click.echo("SUMMARY")
            click.echo("="*50)
            click.echo(f"Total Questions Generated: {len(results)}")
            click.echo(f"Mathematically Correct: {accurate_count} ({accurate_count/len(results)*100:.1f}%)")
            click.echo("="*50)
        
        # Handle output
        if output_json:
            json_output = {"questions": results} if count > 1 else results[0]
            if count > 1 and evaluate:
                json_output["summary"] = {
                    "total": len(results),
                    "accurate": accurate_count,
                    "accuracy_rate": accurate_count/len(results) if results else 0
                }
            click.echo(json.dumps(json_output, indent=2))
        
        # Save to file if requested
        if output:
            file_output = {
                "questions": results,
                "summary": {
                    "total": len(results),
                    "accurate": accurate_count if evaluate else None,
                    "accuracy_rate": accurate_count/len(results) if evaluate and results else None
                }
            }
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
        click.echo("\n" + "="*50)
        click.echo("Question:")
        click.echo("="*50)
        click.echo(question.format_for_display())
        click.echo(f"\nCorrect Answer: {question.answer}")
        
        click.echo("\n" + "-"*50)
        click.echo("Accuracy Evaluation:")
        click.echo("-"*50)
        click.echo(f"Mathematically Correct: {'✓' if result['correct'] else '✗'}")
        click.echo(f"Explanation: {result['explanation']}")
        if result.get('solution_steps'):
            click.echo(f"\nSolution Steps:\n{result['solution_steps']}")
        click.echo("-"*50)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()



if __name__ == '__main__':
    cli()