#!/usr/bin/env python3
import click
import json
from dotenv import load_dotenv

from models.question import Question
from generators.question_generator import QuestionGenerator
from evaluators.accuracy import AccuracyEvaluator
from evaluators.authenticity import AuthenticityEvaluator
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


@cli.group()
def evaluate():
    """Evaluate generated questions using various metrics"""
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


@evaluate.command()
@click.option('--count', '-n', default=10, help='Number of questions to evaluate')
@click.option('--input', 'input_file', type=click.Path(exists=True), help='Load questions from JSON file')
@click.option('--output', '-o', type=click.File('w'), help='Save results to file')
@click.option('--quiet', is_flag=True, help='Show summary only')
def accuracy(count, input_file, output, quiet):
    """Evaluate mathematical accuracy of questions"""
    
    try:
        # Load or generate questions
        if input_file:
            click.echo(f"Loading questions from {input_file}...")
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Handle different formats
            if isinstance(data, dict) and 'questions' in data:
                questions_data = data['questions']
            elif isinstance(data, list):
                questions_data = data
            else:
                questions_data = [data]
            
            # Convert to Question objects
            questions = []
            for q in questions_data[:count]:
                questions.append(Question(
                    question=q.get('question', q.get('content', '')),
                    choices=q['choices'],
                    answer=q.get('answer', q.get('correct_answer', ''))
                ))
        else:
            click.echo(f"Generating {count} SAT math questions...")
            generator = QuestionGenerator()
            questions = generator.generate_questions(count)
        
        # Evaluate questions
        click.echo("Evaluating accuracy...")
        evaluator = AccuracyEvaluator()
        results = []
        correct_count = 0
        
        for i, question in enumerate(questions, 1):
            if not quiet:
                display_question(question, i, len(questions))
            
            result = evaluator.evaluate(question)
            
            if result['correct']:
                correct_count += 1
            
            if not quiet:
                display_evaluation(result)
            
            results.append({
                "question": question.question,
                "choices": question.choices,
                "answer": question.answer,
                "evaluation": result
            })
        
        # Display summary
        if not quiet or len(questions) > 1:
            display_section_header("ACCURACY EVALUATION SUMMARY")
            click.echo(f"Total Questions: {len(questions)}")
            click.echo(f"Mathematically Correct: {correct_count} ({correct_count/len(questions)*100:.1f}%)")
            click.echo("=" * 50)
        
        # Save results if requested
        if output:
            json.dump({
                "results": results,
                "summary": {
                    "total": len(questions),
                    "correct": correct_count,
                    "accuracy_rate": correct_count/len(questions) if questions else 0
                }
            }, output, indent=2)
            click.echo(f"\nResults saved to: {output.name}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()



@evaluate.command()
@click.option('--count', '-n', default=10, help='Number of generated questions to test')
@click.option('--real-questions', type=click.Path(exists=True), default='data/real_questions.json', help='Path to real questions JSON file')
@click.option('--generated-questions', type=click.Path(exists=True), help='Path to pre-generated questions JSON file (optional)')
@click.option('--output', '-o', type=click.File('w'), help='Save results to file')
def authenticity(count, real_questions, generated_questions, output):
    """Test how well generated questions match real SAT questions"""
    
    try:
        # Load real questions
        click.echo(f"Loading real questions from {real_questions}...")
        with open(real_questions, 'r') as f:
            real_qs = json.load(f)
        
        if len(real_qs) < count:
            click.echo(f"Warning: Only {len(real_qs)} real questions available, adjusting count.")
            count = len(real_qs)
        
        # Load or generate fake questions
        if generated_questions:
            click.echo(f"Loading generated questions from {generated_questions}...")
            with open(generated_questions, 'r') as f:
                gen_data = json.load(f)
            
            # Handle both single question and list of questions format
            if isinstance(gen_data, dict) and 'questions' in gen_data:
                gen_data = gen_data['questions']
            elif isinstance(gen_data, dict):
                gen_data = [gen_data]
            
            # Convert to Question objects
            generated_qs = []
            for q in gen_data[:count]:
                # Handle different field names (question vs content, answer vs correct_answer)
                question_text = q.get('question', q.get('content', ''))
                answer = q.get('answer', q.get('correct_answer', ''))
                generated_qs.append(Question(
                    question=question_text,
                    choices=q['choices'],
                    answer=answer
                ))
            
            if len(generated_qs) < count:
                click.echo(f"Warning: Only {len(generated_qs)} generated questions available, adjusting count.")
                count = len(generated_qs)
        else:
            click.echo(f"Generating {count} SAT math questions...")
            generator = QuestionGenerator()
            generated_qs = generator.generate_questions(count)
        
        # Run authenticity evaluation
        click.echo("\nRunning authenticity evaluation...")
        evaluator = AuthenticityEvaluator()
        results = evaluator.evaluate(real_qs[:count], generated_qs)
        
        # Display results
        display_section_header("AUTHENTICITY TEST RESULTS")
        
        summary = results['summary']
        click.echo(f"Total Questions: {summary['total_questions']}")
        click.echo(f"Correct Predictions: {summary['correct_predictions']} / {summary['total_questions']}")
        click.echo(f"Overall Accuracy: {summary['accuracy_percentage']:.1f}%")
        
        click.echo("\nBreakdown:")
        click.echo(f"- Real Questions: {summary['real_questions']['correctly_identified']} / {summary['real_questions']['count']} correctly identified ({summary['real_questions']['accuracy']*100:.1f}%)")
        click.echo(f"- Generated Questions: {summary['generated_questions']['correctly_identified']} / {summary['generated_questions']['count']} correctly identified ({summary['generated_questions']['accuracy']*100:.1f}%)")
        
        click.echo("\nInterpretation:")
        if summary['accuracy_percentage'] < 60:
            click.echo("✓ Excellent! The AI has difficulty distinguishing generated from real questions.")
        elif summary['accuracy_percentage'] < 70:
            click.echo("✓ Good! Generated questions are fairly authentic.")
        elif summary['accuracy_percentage'] < 80:
            click.echo("⚠ Fair. Generated questions have some distinguishable patterns.")
        else:
            click.echo("✗ Poor. Generated questions are easily distinguishable from real ones.")
        
        click.echo("=" * 50)
        
        # Save results if requested
        if output:
            json.dump(results, output, indent=2)
            click.echo(f"\nResults saved to: {output.name}")
        
    except FileNotFoundError:
        click.echo(f"Error: Real questions file not found at {real_questions}", err=True)
        click.echo("Please run extract_real_questions.py first to generate the real questions dataset.", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()