

def save_data(best_entries, entry_reference, question_reference, 
             data_csv, data_txt, entry_id_column, question_id_column,
             number_questions, number_nan, reference_path, mpf_path):
    
    entries_unique = data_csv[[entry_id_column]].drop_duplicates()
    questions_unique = best_entries[[question_id_column]].drop_duplicates()

    entry_reference = entries_unique.merge(entry_reference, 
                                        on = entry_id_column, 
                                        how = 'inner').sort_values(entry_id_column)
    question_reference = questions_unique.merge(question_reference, 
                                                on = question_id_column,
                                                how = 'inner').sort_values(question_id_column)

    nrows = len(data_csv) 
    entries_unique = len(entries_unique)

    identifier = f'questions_{number_questions}_maxna_{number_nan}_nrows_{nrows}_entries_{entries_unique}'
    direct_reference_outname = os.path.join(reference_path, f'direct_reference_{identifier}.csv')
    matrix_outname = os.path.join(mpf_path, f'matrix_{identifier}.txt')
    entry_reference_outname = os.path.join(reference_path, f'entry_reference_{identifier}.csv')
    question_reference_outname = os.path.join(reference_path, f'question_reference_{identifier}.csv')

    # save 
    data_csv.to_csv(direct_reference_outname, index = False)
    data_txt.to_csv(matrix_outname, sep = ' ', header = False, index = False)
    entry_reference.to_csv(entry_reference_outname, index = False)
    question_reference.to_csv(question_reference_outname, index = False)
    

def save_output(best_entries, entry_reference_df, question_reference_df, 
                direct_reference_df, matrix_data, 
                entry_id_column, question_id_column, num_questions, num_nan, 
                reference_folder, mpf_folder):

    unique_entries = direct_reference_df[[entry_id_column]].drop_duplicates()
    unique_questions = best_entries[[question_id_column]].drop_duplicates()
    entry_reference_df = unique_entries.merge(entry_reference_df, on=entry_id_column, how='inner') \
                                      .sort_values(entry_id_column)
    question_reference_df = unique_questions.merge(question_reference_df, on=question_id_column, how='inner') \
                                            .sort_values(question_id_column)

    num_rows = len(direct_reference_df)
    num_unique_entries = len(unique_entries)
    identifier = f'questions_{num_questions}_maxna_{num_nan}_rows_{num_rows}_entries_{num_unique_entries}'
    direct_reference_file = os.path.join(reference_folder, f'direct_reference_{identifier}.csv')
    matrix_file = os.path.join(mpf_folder, f'matrix_{identifier}.txt')
    entry_reference_file = os.path.join(reference_folder, f'entry_reference_{identifier}.csv')
    question_reference_file = os.path.join(reference_folder, f'question_reference_{identifier}.csv')

    direct_reference_df.to_csv(direct_reference_file, index=False)
    matrix_data.to_csv(matrix_file, sep=' ', header=False, index=False)
    entry_reference_df.to_csv(entry_reference_file, index=False)
    question_reference_df.to_csv(question_reference_file, index=False)