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
def generate(evaluate, output_json, count):
    """Generate SAT math question(s)"""
    
    try:
        # Generate question(s)
        generator = QuestionGenerator()
        
        if count == 1:
            click.echo("Generating SAT math question...")
            questions = [generator.generate_question()]
        else:
            click.echo(f"Generating {count} SAT math questions...")
            questions = generator.generate_questions(count)
        
        # Process and display questions
        evaluator = AccuracyEvaluator() if evaluate else None
        results = []
        
        for i, question in enumerate(questions, 1):
            if output_json:
                result = {
                    "id": question.id,
                    "content": question.content,
                    "choices": question.choices,
                    "correct_answer": question.correct_answer
                }
            else:
                if count > 1:
                    click.echo(f"\n{'='*50}")
                    click.echo(f"Question {i}/{count}:")
                    click.echo("="*50)
                else:
                    click.echo("\n" + "="*50)
                    click.echo("Generated Question:")
                    click.echo("="*50)
                click.echo(question.format_for_display())
                click.echo(f"\nCorrect Answer: {question.correct_answer}")
                click.echo("="*50)
            
            # Evaluate if requested
            if evaluate:
                if not output_json:
                    click.echo("\nEvaluating accuracy...")
                evaluation = evaluator.evaluate(question)
                
                if output_json:
                    result["evaluation"] = evaluation
                else:
                    click.echo("\n" + "-"*50)
                    click.echo("Accuracy Evaluation:")
                    click.echo("-"*50)
                    click.echo(f"Mathematically Correct: {'✓' if evaluation['correct'] else '✗'}")
                    click.echo(f"Explanation: {evaluation['explanation']}")
                    if evaluation.get('solution_steps'):
                        click.echo(f"\nSolution Steps:\n{evaluation['solution_steps']}")
                    click.echo("-"*50)
            
            if output_json:
                results.append(result)
        
        if output_json:
            output = {"questions": results} if count > 1 else results[0]
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
        click.echo(f"Mathematically Correct: {'✓' if result['correct'] else '✗'}")
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
    
    # Use the new efficient multi-question generation
    if count <= 10:
        # Generate all at once for small batches
        with click.progressbar(length=1, label='Generating questions') as bar:
            try:
                questions = generator.generate_questions(count)
                bar.update(1)
            except Exception as e:
                click.echo(f"\nError generating questions: {e}", err=True)
                questions = []
    else:
        # For larger batches, generate in chunks of 10
        questions = []
        chunks = (count + 9) // 10  # Round up division
        with click.progressbar(range(chunks), label='Generating questions') as bar:
            for chunk in bar:
                remaining = count - len(questions)
                chunk_size = min(10, remaining)
                try:
                    chunk_questions = generator.generate_questions(chunk_size)
                    questions.extend(chunk_questions)
                except Exception as e:
                    click.echo(f"\nError generating chunk {chunk+1}: {e}", err=True)
    
    # Evaluate questions
    with click.progressbar(questions, label='Evaluating accuracy') as bar:
        for question in bar:
            try:
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
                click.echo(f"\nError evaluating question: {e}", err=True)
    
    # Display summary
    click.echo(f"\n\nGeneration Complete!")
    click.echo(f"Total Questions: {len(results)}")
    click.echo(f"Mathematically Accurate: {accurate_count} ({accurate_count/len(results)*100:.1f}%)")
    
    # Save to file if requested
    if output:
        json.dump({
            "questions": results,
            "summary": {
                "total": len(results),
                "accurate": accurate_count,
                "accuracy_rate": accurate_count/len(results) if results else 0
            }
        }, output, indent=2)
        click.echo(f"\nResults saved to: {output.name}")
    

if __name__ == '__main__':
    cli()