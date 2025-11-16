"""
Homework Grading Service - Automatically grade student homework submissions.
"""
import re
from typing import Dict, List
from openai import OpenAI
from config import Config


class HomeworkGradingService:
    """
    Service for grading homework submissions with partial credit support.
    Uses GPT-4o to analyze student solutions and assign grades.
    """
    
    def __init__(self):
        """Initialize the homework grading service."""
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
        self.model = "gpt-4o"
        self.temperature = 0.3  # Low temperature for consistent grading
    
    def _extract_exercises_from_homework(self, homework_html: str) -> List[Dict]:
        """
        Extract individual exercises from homework HTML.
        
        Args:
            homework_html: The homework content in HTML format
            
        Returns:
            List of exercise dictionaries with number, content, and max_points
        """
        exercises = []
        
        # Pattern to match exercise blocks
        exercise_pattern = r'<div class="exercise">.*?<span class="exercise-number">Exercițiul (\d+)</span>.*?<span class="points">\((\d+(?:\.\d+)?)\s*puncte\)</span>.*?<div class="exercise-content">(.*?)</div>.*?</div>'
        
        matches = re.finditer(exercise_pattern, homework_html, re.DOTALL)
        
        for match in matches:
            exercise_num = int(match.group(1))
            max_points = float(match.group(2))
            content = match.group(3).strip()
            
            # Clean HTML tags from content for better readability
            clean_content = re.sub('<[^<]+?>', ' ', content)
            clean_content = ' '.join(clean_content.split())
            
            exercises.append({
                "exercise_number": exercise_num,
                "content": clean_content,
                "max_points": max_points
            })
        
        return exercises
    
    def _round_to_quarter(self, score: float) -> float:
        """
        Round a score to the nearest 0.25 multiple.
        
        Args:
            score: The raw score
            
        Returns:
            Score rounded to nearest 0.25
        """
        return round(score * 4) / 4
    
    def _verify_mathematical_answer(self, exercise_content: str, student_solution: str) -> Dict:
        """
        Verify if a mathematical answer is arithmetically correct.
        
        Args:
            exercise_content: The exercise question
            student_solution: The student's solution
            
        Returns:
            Dictionary with verification results
        """
        verification_prompt = f"""You are a mathematics verification expert. Your ONLY job is to check if the arithmetic and algebra in the student's solution is correct.

EXERCISE:
{exercise_content}

STUDENT'S SOLUTION:
{student_solution}

VERIFICATION TASK:
1. Extract the final answer from the student's solution
2. Check if all arithmetic calculations are correct
3. For equations: Verify the solution by substituting back into the original equation
4. Identify any calculation errors

Provide your verification in this EXACT format:

FINAL_ANSWER: [the student's final answer, e.g., "x = 8" or "20 lei"]
ARITHMETIC_CORRECT: [YES or NO]
ERRORS_FOUND: [list any calculation errors, or "None" if correct]
CORRECT_ANSWER: [what the correct answer should be if student is wrong, or "Same as student" if correct]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,  # Very low for factual verification
                max_tokens=500
            )
            
            verification_text = response.choices[0].message.content
            
            # Parse verification results
            is_correct = "ARITHMETIC_CORRECT: YES" in verification_text
            errors = re.search(r'ERRORS_FOUND:(.*?)(?:\n[A-Z_]+:|$)', verification_text, re.DOTALL)
            errors_text = errors.group(1).strip() if errors else ""
            
            return {
                "is_arithmetically_correct": is_correct,
                "errors_found": errors_text,
                "verification_text": verification_text
            }
        
        except Exception as e:
            # If verification fails, assume no verification was possible
            return {
                "is_arithmetically_correct": None,
                "errors_found": "",
                "verification_text": f"Verification failed: {str(e)}"
            }
    
    def grade_single_exercise(
        self,
        exercise_content: str,
        student_solution: str,
        max_points: float
    ) -> Dict:
        """
        Grade a single exercise with partial credit.
        
        Args:
            exercise_content: The exercise question/prompt
            student_solution: The student's submitted solution
            max_points: Maximum points for this exercise
            
        Returns:
            Dictionary with:
                - points_earned: float (rounded to 0.25)
                - max_points: float
                - percentage: float
                - feedback: str
                - is_correct: bool
                - is_partial: bool
        """
        prompt = f"""You are an experienced Romanian teacher grading a student's homework exercise with strict attention to detail.

EXERCISE:
{exercise_content}

STUDENT'S SOLUTION:
{student_solution}

GRADING INSTRUCTIONS:
1. Carefully analyze EVERY step and the FINAL ANSWER
2. Verify calculations are arithmetically correct
3. Check if the final answer is mathematically correct
4. Determine what percentage of the exercise was solved correctly (0-100%)
5. Award partial credit based on:
   - Correct methodology and approach: up to 50%
   - Correct intermediate steps: up to 25%
   - Correct final answer: up to 25%
6. If the final answer is WRONG (even if methodology is right), maximum score is 75%
7. If methodology is wrong but answer is accidentally correct, maximum score is 50%
8. Calculate points: (percentage_correct / 100) * {max_points}
9. The final score will be rounded to the nearest 0.25

IMPORTANT:
- For math problems: Verify arithmetic! If 4x = 20, then x = 5 (not 8)
- For equations: Check if the solution satisfies the original equation
- Be strict but fair - reward good process even if final answer has calculation errors

Provide your grading in the following format:

PERCENTAGE_CORRECT: [number between 0-100]
POINTS_CALCULATION: [show your calculation]
FEEDBACK: [Provide constructive feedback in Romanian explaining what the student did correctly, what was incorrect or missing (be specific about errors), and how they can improve]

CRITICAL: The FEEDBACK section is MANDATORY and must be detailed and helpful. Write at least 2-3 sentences.

Be fair, consistent, strict on arithmetic accuracy, and educational in your grading."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Debug: print the response to see what we're getting
            print(f"\n--- Grading Response for Exercise ---")
            print(response_text[:500] if len(response_text) > 500 else response_text)
            print("--- End Response ---\n")
            
            # Parse the response with improved regex
            percentage_match = re.search(r'PERCENTAGE_CORRECT:\s*(\d+(?:\.\d+)?)', response_text)
            
            # Try multiple feedback patterns to be more robust
            feedback_match = re.search(r'FEEDBACK:\s*(.*?)(?:\n\n[A-Z_]+:|$)', response_text, re.DOTALL)
            if not feedback_match:
                feedback_match = re.search(r'FEEDBACK:(.*)', response_text, re.DOTALL)
            
            # Extract percentage
            if percentage_match:
                percentage = float(percentage_match.group(1))
                percentage = max(0, min(100, percentage))  # Clamp to 0-100
            else:
                percentage = 0
            
            # Extract feedback - try multiple methods
            if feedback_match:
                feedback = feedback_match.group(1).strip()
                # Remove any trailing section markers
                feedback = re.sub(r'\n\n[A-Z_]+:.*$', '', feedback, flags=re.DOTALL).strip()
            else:
                # Fallback: extract everything after FEEDBACK: until end or next section
                lines = response_text.split('\n')
                feedback_lines = []
                in_feedback = False
                for line in lines:
                    if 'FEEDBACK:' in line:
                        in_feedback = True
                        # Include text after FEEDBACK: on same line
                        after_marker = line.split('FEEDBACK:', 1)[1].strip()
                        if after_marker:
                            feedback_lines.append(after_marker)
                        continue
                    if in_feedback:
                        if re.match(r'^[A-Z_]+:', line):  # Next section started
                            break
                        feedback_lines.append(line)
                feedback = '\n'.join(feedback_lines).strip()
            
            # If still no feedback, use a default
            if not feedback or len(feedback) < 10:
                feedback = "Nu s-a putut genera feedback detaliat."
            
            # For mathematical exercises, do additional verification
            verification = self._verify_mathematical_answer(exercise_content, student_solution)
            
            # If verification shows arithmetic error and AI gave 100%, override to partial credit
            if verification["is_arithmetically_correct"] is False and percentage >= 95:
                # Cap at 75% if final answer is wrong but method is correct
                percentage = min(percentage, 75)
                
                # Append arithmetic error to feedback
                if verification["errors_found"] and "None" not in verification["errors_found"]:
                    feedback_suffix = f"\n\n⚠️ Atenție: Am detectat o eroare de calcul: {verification['errors_found']}"
                    feedback = feedback + feedback_suffix if feedback else feedback_suffix
            
            # Calculate points and round to 0.25
            raw_points = (percentage / 100) * max_points
            points_earned = self._round_to_quarter(raw_points)
            
            # Ensure we don't exceed max points due to rounding
            points_earned = min(points_earned, max_points)
            
            is_correct = points_earned >= max_points * 0.95  # 95% or more is considered fully correct
            is_partial = 0 < points_earned < max_points * 0.95
            
            return {
                "points_earned": points_earned,
                "max_points": max_points,
                "percentage": percentage,
                "feedback": feedback,
                "is_correct": is_correct,
                "is_partial": is_partial
            }
        
        except Exception as e:
            return {
                "points_earned": 0.0,
                "max_points": max_points,
                "percentage": 0.0,
                "feedback": f"Eroare la evaluare: {str(e)}",
                "is_correct": False,
                "is_partial": False,
                "error": str(e)
            }
    
    def grade_homework(
        self,
        homework_html: str,
        parsed_submission: str,
        subject: str = "",
        grade: int = None
    ) -> Dict:
        """
        Grade a complete homework submission.
        
        Args:
            homework_html: The original homework assignment in HTML format
            parsed_submission: The parsed text from student's PDF submission
            subject: Subject name (optional, for context)
            grade: Grade level (optional, for context)
            
        Returns:
            Dictionary with:
                - total_points_earned: float
                - total_points_possible: float
                - final_grade_percentage: float
                - exercises: list of graded exercise results
                - overall_feedback: str
        """
        # Extract exercises from homework
        exercises = self._extract_exercises_from_homework(homework_html)
        
        if not exercises:
            return {
                "success": False,
                "error": "Nu s-au putut extrage exercițiile din tema de casă."
            }
        
        # Split parsed submission into sections (try to identify exercise boundaries)
        submission_sections = self._split_submission_by_exercises(
            parsed_submission,
            len(exercises)
        )
        
        # Grade each exercise
        graded_exercises = []
        total_earned = 0.0
        total_possible = 0.0
        
        for i, exercise in enumerate(exercises):
            exercise_num = exercise["exercise_number"]
            exercise_content = exercise["content"]
            max_points = exercise["max_points"]
            
            # Get corresponding student solution
            student_solution = submission_sections.get(exercise_num, "[LIPSEȘTE SOLUȚIA]")
            
            print(f"Grading Exercise {exercise_num}...")
            
            # Grade the exercise
            result = self.grade_single_exercise(
                exercise_content=exercise_content,
                student_solution=student_solution,
                max_points=max_points
            )
            
            graded_exercises.append({
                "exercise_number": exercise_num,
                "exercise_content": exercise_content,
                "student_solution": student_solution,
                **result
            })
            
            total_earned += result["points_earned"]
            total_possible += result["max_points"]
        
        # Calculate final grade
        final_percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        # Generate overall feedback
        overall_feedback = self._generate_overall_feedback(
            graded_exercises,
            total_earned,
            total_possible,
            final_percentage
        )
        
        return {
            "success": True,
            "total_points_earned": round(total_earned, 2),
            "total_points_possible": round(total_possible, 2),
            "final_grade_percentage": round(final_percentage, 2),
            "exercises": graded_exercises,
            "overall_feedback": overall_feedback,
            "subject": subject,
            "grade_level": grade
        }
    
    def _split_submission_by_exercises(
        self,
        parsed_submission: str,
        num_exercises: int
    ) -> Dict[int, str]:
        """
        Split parsed submission text into sections by exercise number.
        
        Args:
            parsed_submission: The full parsed submission text
            num_exercises: Expected number of exercises
            
        Returns:
            Dictionary mapping exercise number to solution text
        """
        sections = {}
        
        # Try to find exercise markers
        lines = parsed_submission.split('\n')
        current_exercise = None
        current_content = []
        
        for line in lines:
            # Look for exercise markers (various formats)
            exercise_match = re.search(r'(?:Exercițiul|Exercitiul|Ex\.?|E\.?)\s*(\d+)', line, re.IGNORECASE)
            
            if exercise_match:
                # Save previous exercise
                if current_exercise is not None:
                    sections[current_exercise] = '\n'.join(current_content).strip()
                
                # Start new exercise
                current_exercise = int(exercise_match.group(1))
                current_content = [line]
            elif current_exercise is not None:
                current_content.append(line)
        
        # Save last exercise
        if current_exercise is not None:
            sections[current_exercise] = '\n'.join(current_content).strip()
        
        # If no exercises were detected, try to split evenly
        if not sections and num_exercises > 0:
            lines_per_exercise = len(lines) // num_exercises
            for i in range(1, num_exercises + 1):
                start_idx = (i - 1) * lines_per_exercise
                end_idx = start_idx + lines_per_exercise if i < num_exercises else len(lines)
                sections[i] = '\n'.join(lines[start_idx:end_idx]).strip()
        
        return sections
    
    def _generate_overall_feedback(
        self,
        graded_exercises: List[Dict],
        total_earned: float,
        total_possible: float,
        final_percentage: float
    ) -> str:
        """Generate overall feedback for the homework."""
        correct_count = sum(1 for ex in graded_exercises if ex["is_correct"])
        partial_count = sum(1 for ex in graded_exercises if ex["is_partial"])
        incorrect_count = len(graded_exercises) - correct_count - partial_count
        
        feedback_parts = []
        
        # Overall performance
        feedback_parts.append(f"**Nota finală: {total_earned}/{total_possible} puncte ({final_percentage:.1f}%)**\n")
        
        # Summary
        feedback_parts.append(f"**Sumar:**")
        feedback_parts.append(f"- Exerciții corecte: {correct_count}/{len(graded_exercises)}")
        if partial_count > 0:
            feedback_parts.append(f"- Exerciții parțial corecte: {partial_count}/{len(graded_exercises)}")
        if incorrect_count > 0:
            feedback_parts.append(f"- Exerciții incorecte: {incorrect_count}/{len(graded_exercises)}")
        
        # Performance evaluation
        feedback_parts.append("\n**Evaluare generală:**")
        if final_percentage >= 90:
            feedback_parts.append("Excellent! Ai demonstrat o înțelegere foarte bună a materiei.")
        elif final_percentage >= 75:
            feedback_parts.append("Foarte bine! Ai o înțelegere solidă, cu mici aspecte de îmbunătățit.")
        elif final_percentage >= 60:
            feedback_parts.append("Bine. Ai înțeles conceptele de bază, dar mai sunt aspecte de aprofundat.")
        elif final_percentage >= 50:
            feedback_parts.append("Suficient. Recomand să revizuiești materialul și să exersezi mai mult.")
        else:
            feedback_parts.append("Trebuie să lucrezi mai mult la această temă. Recomand să studiezi din nou lecția și să ceri ajutor dacă este necesar.")
        
        return '\n'.join(feedback_parts)
