package org.apache.maven.tools.repoclean.rewrite;

/*
 * Copyright 2001-2005 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.maven.artifact.Artifact;
import org.apache.maven.model.Model;
import org.apache.maven.model.io.xpp3.MavenXpp3Reader;
import org.apache.maven.model.io.xpp3.MavenXpp3Writer;
import org.apache.maven.tools.repoclean.report.Reporter;
import org.codehaus.plexus.util.StringUtils;

import java.io.Reader;
import java.io.Writer;

/**
 * @author jdcasey
 */
public class V4PomRewriter
    implements ArtifactPomRewriter
{
    public void rewrite( Artifact artifact, Reader from, Writer to, Reporter reporter, boolean reportOnly )
        throws Exception
    {
        Model model = null;

        if ( from != null )
        {
            MavenXpp3Reader reader = new MavenXpp3Reader();

            try
            {
                model = reader.read( from );
            }
            catch ( Exception e )
            {
                reporter.error( "Invalid v4 POM at \'" + from + "\'. Cannot read.", e );
            }
        }
        else
        {
            model = new Model();
        }

        if ( model != null )
        {
            validateBasics( model, artifact, reporter );

            if ( !reportOnly )
            {
                MavenXpp3Writer writer = new MavenXpp3Writer();
                writer.write( to, model );
            }
        }
    }

    private void validateBasics( Model model, Artifact artifact, Reporter reporter )
        throws Exception
    {
        if ( StringUtils.isEmpty( model.getModelVersion() ) )
        {
            model.setModelVersion( "4.0.0" );
        }

        if ( StringUtils.isEmpty( model.getGroupId() ) )
        {
            reporter.warn( "Setting groupId on model using artifact information." );
            model.setGroupId( artifact.getGroupId() );
        }

        if ( StringUtils.isEmpty( model.getArtifactId() ) )
        {
            reporter.warn( "Setting artifactId on model using artifact information." );
            model.setArtifactId( artifact.getArtifactId() );
        }

        if ( StringUtils.isEmpty( model.getVersion() ) )
        {
            reporter.warn( "Setting version on model using artifact information." );
            model.setVersion( artifact.getVersion() );
        }

        if ( StringUtils.isEmpty( model.getPackaging() ) )
        {
            reporter.warn( "Setting packaging on model using artifact type information." );
            model.setPackaging( artifact.getType() );
        }
    }

}